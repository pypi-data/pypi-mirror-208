/***************************************************************************************************
 * Copyright (c) 2023, Tri Dao.
 ******************************************************************************/

#pragma once

#include <cute/algorithm/copy.hpp>
#include <cute/algorithm/gemm.hpp>

#include <cutlass/cutlass.h>
#include <cutlass/array.h>
#include <cutlass/numeric_types.h>
#include <cutlass/numeric_conversion.h>

#include "block_info.h"
#include "kernel_traits.h"
#include "utils.h"
#include "softmax.h"
#include "philox.cuh"

namespace flash {

using namespace cute;

////////////////////////////////////////////////////////////////////////////////////////////////////

template <int THREADS_PER_ROW, typename elem_type=cutlass::half_t, typename Engine0, typename Layout0,
          typename Engine1, typename Layout1, typename Engine2, typename Layout2>
inline __device__ void dot_do_o(Tensor<Engine0, Layout0> const &do_, Tensor<Engine0, Layout0> const &o,
                                Tensor<Engine1, Layout1> &gdPsum, Tensor<Engine2, Layout2> &sdPsum,
                                const int gdP_col_stride, const float scale) {
    static_assert(Layout0::rank == 3, "Only support 3D Tensor");
    static_assert(Layout1::rank == 1, "Only support 1D Tensor");
    // Reshape do_ and o from (8, kBlockM / 32, kHeadDim / 64) to (kBlockM / 32, 8 * kHeadDim / 64)
    CUTE_STATIC_ASSERT_V(do_.layout() == o.layout());
    Tensor do_reshaped = make_tensor(do_.data(), make_layout(get<1>(do_.layout()),
                                                             make_layout(get<0>(do_.layout()),
                                                                         get<2>(do_.layout()))));
    Tensor o_reshaped = make_tensor(o.data(), do_reshaped.layout());
    constexpr int kNCols = size<1>(do_reshaped);
    cutlass::NumericArrayConverter<float, elem_type, kNCols> convert;
    #pragma unroll
    for (int mi = 0; mi < size<0>(do_reshaped); ++mi) {
        auto do_fp32 = convert(*reinterpret_cast<const cutlass::Array<elem_type, kNCols>*>(do_reshaped(mi, _).data()));
        auto o_fp32 = convert(*reinterpret_cast<const cutlass::Array<elem_type, kNCols>*>(o_reshaped(mi, _).data()));
        float dP_sum = do_fp32[0] * o_fp32[0];
        #pragma unroll
        for (int ni = 1; ni < kNCols; ni++) {
            dP_sum += do_fp32[ni] * o_fp32[ni];
        }
        flash::SumOp<float> sum_op;
        dP_sum = flash::Allreduce<THREADS_PER_ROW>::run(dP_sum, sum_op) * scale;
        // TODO: when we change headdim from {32, 64, 128} to 96, this indexing should change
        if (threadIdx.x % THREADS_PER_ROW == 0) {
            gdPsum(mi * gdP_col_stride + threadIdx.x / THREADS_PER_ROW) = dP_sum;
            // recast<float>(sdPsum)(mi * gdP_col_stride + threadIdx.x / THREADS_PER_ROW) = dP_sum;
        }
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, bool Is_first, bool Is_last, bool Seq_parallel=false, typename Params, typename Prng>
inline __device__ void compute_dq_dk_dv_1Nblock(const Params &params, const int bidb, const int bidh, Prng &ph, const int n_block) {

    using X = Underscore;

    using Element = typename Kernel_traits::Element;
    using ElementAccum = typename Kernel_traits::ElementAccum;

    // Shared memory.
    extern __shared__ char smem_[];

    // The thread index.
    const int tidx = threadIdx.x;

    // TODO: change this when we need to deal with seqlen not a multiple of 128
    const BlockInfo</*Varlen=*/false> binfo(params, bidb);
    // if( binfo.stop_early(n_block * Cta_tile_p::N) ) return;

    // flash::Mask<Cta_tile_p, Is_causal> mask(binfo, tidx, n_block);

    constexpr int kBlockM = Kernel_traits::kBlockM;
    constexpr int kBlockN = Kernel_traits::kBlockN;
    constexpr int kHeadDim = Kernel_traits::kHeadDim;
    constexpr int S_MMA_M = kBlockM / decltype(size<0>(typename Kernel_traits::TiledMmaSdP::TiledShape_MNK{}))::value;
    constexpr int AtomLayoutMS = Kernel_traits::AtomLayoutMSdP;

    const uint32_t row_offset_q = binfo.q_offset(params.q_batch_stride_in_elts, params.q_row_stride_in_elts, bidb)
        + bidh * params.q_head_stride_in_elts;
    const uint32_t row_offset_k = binfo.k_offset(params.k_batch_stride_in_elts, params.k_row_stride_in_elts, bidb)
        + n_block * kBlockN * params.k_row_stride_in_elts + bidh * params.k_head_stride_in_elts;
    const uint32_t row_offset_v = binfo.k_offset(params.v_batch_stride_in_elts, params.v_row_stride_in_elts, bidb)
        + n_block * kBlockN * params.v_row_stride_in_elts + bidh * params.v_head_stride_in_elts;
    const uint32_t row_offset_do = binfo.q_offset(params.do_batch_stride_in_elts, params.do_row_stride_in_elts, bidb)
        + bidh * params.do_head_stride_in_elts;
    const uint32_t row_offset_o = binfo.q_offset(params.o_batch_stride_in_elts, params.o_row_stride_in_elts, bidb)
        + bidh * params.o_head_stride_in_elts;
    const uint32_t row_offset_dq = binfo.q_offset(params.dq_batch_stride_in_elts, params.dq_row_stride_in_elts, bidb)
        + bidh * params.dq_head_stride_in_elts;
    // TODO: this needs to change when we seqlen_q is not dividible by 128 etc and headdim is not power of 2.
    const uint32_t row_offset_dq_accum = (bidb * params.h + bidh) * params.seqlen_q * params.d;
    const uint32_t row_offset_summary = (bidb * params.h + bidh) * params.seqlen_q;

    // We assume that params.d == kHeadDim for now
    Tensor gQ = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.q_ptr) + row_offset_q),
                            Shape<Int<kBlockM>, Int<kHeadDim>>{},
                            make_stride(params.q_row_stride_in_elts, _1{}));
    Tensor gK = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.k_ptr) + row_offset_k),
                            Shape<Int<kBlockN>, Int<kHeadDim>>{},
                            make_stride(params.k_row_stride_in_elts, _1{}));
    Tensor gV = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.v_ptr) + row_offset_v),
                            Shape<Int<kBlockN>, Int<kHeadDim>>{},
                            make_stride(params.v_row_stride_in_elts, _1{}));
    Tensor gdO = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.do_ptr) + row_offset_do),
                             Shape<Int<kBlockM>, Int<kHeadDim>>{},
                             make_stride(params.do_row_stride_in_elts, _1{}));
    Tensor gO = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.o_ptr) + row_offset_o),
                            Shape<Int<kBlockM>, Int<kHeadDim>>{},
                            make_stride(params.do_row_stride_in_elts, _1{}));
    // We'll advance the gdQ before the 1st write.
    Tensor gdQ = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.dq_ptr) + row_offset_dq - kBlockM * params.dq_row_stride_in_elts),
                             Shape<Int<kBlockM>, Int<kHeadDim>>{},
                             make_stride(params.dq_row_stride_in_elts, _1{}));
    // We'll advance the gdQ before the 1st read/write.
    Tensor gdQaccum = make_tensor(make_gmem_ptr(reinterpret_cast<ElementAccum *>(params.dq_accum_ptr) + row_offset_dq_accum - kBlockM * params.d),
                                  Shape<Int<kBlockM>, Int<kHeadDim>>{}, Stride<Int<kHeadDim>, _1>{});
    Tensor gLSE = make_tensor(make_gmem_ptr(reinterpret_cast<ElementAccum *>(params.softmax_lse_ptr) + row_offset_summary),
                              Shape<Int<kBlockM>>{}, Stride<_1>{});
    Tensor gdPsum = make_tensor(make_gmem_ptr(reinterpret_cast<ElementAccum *>(params.dsoftmax_sum) + row_offset_summary),
                                 Shape<Int<kBlockM>>{}, Stride<_1>{});

    Tensor sQ = make_tensor(make_smem_ptr(reinterpret_cast<Element *>(smem_)),
                            typename Kernel_traits::SmemLayoutQdO{});
    Tensor sQtransposed = make_tensor(sQ.data(), typename Kernel_traits::SmemLayoutQdOtransposed{});
    Tensor sQtransposedNoSwizzle = make_tensor(sQ.data(),
                                               typename Kernel_traits::SmemLayoutQdOtransposedNoSwizzle{});
    // Double buffer for sQ
    Tensor sdO = make_tensor(sQ.data() + size(sQ) * 2, typename Kernel_traits::SmemLayoutQdO{});
    Tensor sdOtransposed = make_tensor(sdO.data(), typename Kernel_traits::SmemLayoutQdOtransposed{});
    Tensor sdOtransposedNoSwizzle = make_tensor(sdO.data(),
                                                typename Kernel_traits::SmemLayoutQdOtransposedNoSwizzle{});
    Tensor sK = make_tensor(sdO.data() + size(sdO), typename Kernel_traits::SmemLayoutKV{});
    Tensor sV = make_tensor(sK.data() + size(sK), typename Kernel_traits::SmemLayoutKV{});
    Tensor sKtransposed = make_tensor(sK.data(), typename Kernel_traits::SmemLayoutKtransposed{});
    Tensor sKtransposedNoSwizzle = make_tensor(sK.data(),
                                               typename Kernel_traits::SmemLayoutKtransposedNoSwizzle{});
    Tensor sdS = make_tensor(!Kernel_traits::V_IN_REGS ? sV.data() + size(sV) : sK.data() + size(sK),
                             typename Kernel_traits::SmemLayoutPdS{});
    Tensor sdStransposed = make_tensor(sdS.data(), typename Kernel_traits::SmemLayoutPdStransposed{});
    Tensor sdStransposedNoSwizzle = make_tensor(sdS.data(), typename Kernel_traits::SmemLayoutPdStransposedNoSwizzle{});
    Tensor sP = make_tensor(sdS.data() + size(sdS), typename Kernel_traits::SmemLayoutPdS{});
    Tensor sPtransposed = make_tensor(sP.data(), typename Kernel_traits::SmemLayoutPdStransposed{});
    Tensor sPtransposedNoSwizzle = make_tensor(sP.data(), typename Kernel_traits::SmemLayoutPdStransposedNoSwizzle{});
    // sP and sdQ share the same memory so be careful
    Tensor sdQ = make_tensor(sP.data(), typename Kernel_traits::SmemLayoutdQ{});
    Tensor sdPsum = make_tensor(make_smem_ptr(reinterpret_cast<float2 *>((sP.data() + cute::max(size(sP), size(sdQ))).get())),
                                Shape<Int<Kernel_traits::kSmemdPsumCount / 2>>{});

    auto gmem_thr_copy_q = typename Kernel_traits::GmemTiledCopyQ{}.get_thread_slice(tidx);
    auto gmem_thr_copy_kv = typename Kernel_traits::GmemTiledCopyKV{}.get_thread_slice(tidx);
    using GmemTiledCopydO = typename std::conditional<
        Is_first,
        typename Kernel_traits::GmemTiledCopydO,
        typename Kernel_traits::GmemTiledCopyQ
    >::type;
    auto gmem_thr_copy_do = GmemTiledCopydO{}.get_thread_slice(tidx);
    auto gmem_thr_copy_dq = typename Kernel_traits::GmemTiledCopydQ{}.get_thread_slice(tidx);
    using GmemLayoutAtomdQaccum = typename std::conditional<
        !Seq_parallel,
        typename Kernel_traits::GmemTiledCopydQaccum,
        typename Kernel_traits::GmemTiledCopydQaccumAtomicAdd
    >::type;
    auto gmem_thr_copy_dq_accum = GmemLayoutAtomdQaccum{}.get_thread_slice(tidx);

    Tensor tQgQ = gmem_thr_copy_q.partition_S(gQ);
    Tensor tQsQ = gmem_thr_copy_q.partition_D(sQ);
    Tensor tdOgdO = gmem_thr_copy_do.partition_S(gdO);
    Tensor tdOsdO = gmem_thr_copy_do.partition_D(sdO);
    Tensor tdOgO = gmem_thr_copy_do.partition_S(gO);
    Tensor tKgK = gmem_thr_copy_kv.partition_S(gK);  // (KCPY, KCPY_N, KCPY_K)
    Tensor tKsK = gmem_thr_copy_kv.partition_D(sK);
    Tensor tVgV = gmem_thr_copy_kv.partition_S(gV);  // (VCPY, VCPY_N, VCPY_K)
    Tensor tVsV = gmem_thr_copy_kv.partition_D(sV);
    Tensor tdQsdQ = gmem_thr_copy_dq.partition_S(sdQ);    // ((Atom,AtomNum),ATOM_M,ATOM_N)
    Tensor tdQgdQ = gmem_thr_copy_dq.partition_D(gdQ);
    Tensor tdQgdQaccum = gmem_thr_copy_dq_accum.partition_D(gdQaccum);
    // if (cute::thread0()) { print(tdQgdQaccum.layout()); printf("\n"); }
    // __syncthreads();
    // if (blockIdx.x == 0 && blockIdx.y == 0 && blockIdx.z == 0 && tidx < 64) {
    //     printf("tidx = %d, tdQgdQaccum = 0x%p\n", tidx, tdQgdQaccum.data());
    // }

    typename Kernel_traits::TiledMmaSdP tiled_mma_sdp;
    auto thr_mma_sdp = tiled_mma_sdp.get_thread_slice(tidx);
    Tensor tSrQ  = thr_mma_sdp.partition_fragment_A(sQ);         // (MMA,MMA_M,MMA_K)
    // if (cute::thread0()) { print(tSrQ.layout()); }
    Tensor tSrK  = thr_mma_sdp.partition_fragment_B(sK);         // (MMA,MMA_N,MMA_K)
    // if (cute::thread(0, 0) && n_block == 0) { print(tSrK.layout()); printf("\n"); }
    Tensor tdPrdO  = thr_mma_sdp.partition_fragment_A(sdO);      // (MMA,MMA_M,MMA_K)
    Tensor tdPrV  = thr_mma_sdp.partition_fragment_B(sV);        // (MMA,MMA_N,MMA_K)

    typename Kernel_traits::TiledMmadKV tiled_mma_dkv;
    auto thr_mma_dkv = tiled_mma_dkv.get_thread_slice(tidx);
    Tensor tdKrdS  = thr_mma_dkv.partition_fragment_A(sdStransposedNoSwizzle); // (MMA, MMA_N, MMA_M)
    // if (cute::thread0()) { print(tdKrdS.layout()); printf("\n"); }
    Tensor tdKrQ  = thr_mma_dkv.partition_fragment_B(sQtransposedNoSwizzle);   // (MMA, MMA_K, MMA_M)
    // if (cute::thread0()) { print(tdKrQ.layout()); printf("\n"); }
    Tensor tdVrP  = thr_mma_dkv.partition_fragment_A(sPtransposedNoSwizzle);   // (MMA, MMA_N, MMA_M)
    // if (cute::thread0()) { print(tdVrP.layout()); printf("\n"); }
    Tensor tdVrdO  = thr_mma_dkv.partition_fragment_B(sdOtransposedNoSwizzle); // (MMA, MMA_K, MMA_M)
    // if (cute::thread0()) { print(tdVrdO.layout()); printf("\n"); }

    typename Kernel_traits::TiledMmadQ tiled_mma_dq;
    auto thr_mma_dq = tiled_mma_dq.get_thread_slice(tidx);
    Tensor tdQrdS = thr_mma_dq.partition_fragment_A(sdS);                      // (MMA, MMA_M, MMA_N)
    Tensor tdQrK  = thr_mma_dq.partition_fragment_B(sKtransposedNoSwizzle);    // (MMA, MMA_K, MMA_N)

    Tensor acc_dk = partition_fragment_C(tiled_mma_dkv, Shape<Int<kBlockN>, Int<kHeadDim>>{});  // MMA, MMA_N, MMA_K
    Tensor acc_dv = partition_fragment_C(tiled_mma_dkv, Shape<Int<kBlockN>, Int<kHeadDim>>{});  // MMA, MMA_N, MMA_K

    //
    // Copy Atom retiling
    //

    auto smem_thr_copy_QdO = make_tiled_copy_A(typename Kernel_traits::SmemCopyAtomQ{}, tiled_mma_sdp).get_thread_slice(tidx);
    Tensor tSsQ = smem_thr_copy_QdO.partition_S(sQ);
    Tensor tdPsdO = smem_thr_copy_QdO.partition_S(sdO);

    auto smem_tiled_copy_KV = make_tiled_copy_B(typename Kernel_traits::SmemCopyAtomK{}, tiled_mma_sdp);
    // if (cute::thread0()) { printf("HERE\n"); print(tiled_mma_sdp.get_layoutB_TV()); printf("\n"); }
    auto smem_thr_copy_KV = make_tiled_copy_B(typename Kernel_traits::SmemCopyAtomK{}, tiled_mma_sdp).get_thread_slice(tidx);
    Tensor tSsK = smem_thr_copy_KV.partition_S(sK);
    // if (cute::thread(0, 0) && n_block == 0) { print(tSsK.layout()); printf("\n"); }
    Tensor tdPsV = smem_thr_copy_KV.partition_S(sV);

    // Partition sP and sdS to match the accumulator partitioning
    // This has to be tiled_mma_sdp, not tiled_mma_dkv
    auto smem_thr_copy_PdS = make_tiled_copy_C(typename Kernel_traits::SmemCopyAtomPdS{}, tiled_mma_sdp).get_thread_slice(tidx);
    Tensor tPsP = smem_thr_copy_PdS.partition_D(sP);      // ((Atom,AtomNum),PIPE_M,PIPE_N)
    // if (n_block == 0 && cute::thread(0, 0)) { print(tPsP.layout()); printf("\n"); }
    // __syncthreads();
    // if (n_block == 0 && cute::thread(12, 0)) { print(tPsP.layout()); printf("\n"); }
    // __syncthreads();
    // if (n_block == 0 && cute::thread(16, 0)) { print(tPsP.layout()); printf("\n"); }
    // if (n_block == 0 && blockIdx.x == 0 && blockIdx.y == 0 && tidx < 64) {
    //     printf("tidx=%d, tPsP = 0x%p\n", tidx, tPsP.data());
    // }
    Tensor tdSsdS = smem_thr_copy_PdS.partition_D(sdS);   // ((Atom,AtomNum),PIPE_M,PIPE_N)

    auto smem_thr_copy_PdStransposed = make_tiled_copy_A(typename Kernel_traits::SmemCopyAtomPdStransposed{}, tiled_mma_dkv).get_thread_slice(tidx);
    Tensor tdVsP = smem_thr_copy_PdStransposed.partition_S(sPtransposed);
    Tensor tdKsdS = smem_thr_copy_PdStransposed.partition_S(sdStransposed);
    // if (cute::thread0()) { print(tdVsP.layout()); printf("\n"); printf("\n"); }

    auto smem_thr_copy_QdOtransposed = make_tiled_copy_B(typename Kernel_traits::SmemCopyAtomQdOtransposed{}, tiled_mma_dkv).get_thread_slice(tidx);
    Tensor tdVsdO = smem_thr_copy_QdOtransposed.partition_S(sdOtransposed);
    // if (cute::thread0()) { print(tdVsdO.layout()); printf("\n"); printf("\n"); }
    // if (cute::thread0()) { print(tdKsdS.layout()); printf("\n"); printf("\n"); }
    Tensor tdKsQ = smem_thr_copy_QdOtransposed.partition_S(sQtransposed);
    // if (cute::thread0()) { print(tdKsQ.layout()); printf("\n"); printf("\n"); }

    auto smem_thr_copy_dS = make_tiled_copy_A(typename Kernel_traits::SmemCopyAtomdS{}, tiled_mma_dq).get_thread_slice(tidx);
    Tensor tdQsdS = smem_thr_copy_dS.partition_S(sdS);
    // if (cute::thread0()) { print(tdQsdS.layout()); printf("\n"); printf("\n"); }

    auto smem_thr_copy_Ktransposed = make_tiled_copy_B(typename Kernel_traits::SmemCopyAtomKtransposed{}, tiled_mma_dq).get_thread_slice(tidx);
    Tensor tdQsK = smem_thr_copy_Ktransposed.partition_S(sKtransposed);
    // if (cute::thread0()) { print(tdQsK.layout()); printf("\n"); printf("\n"); }

    auto smem_thr_copy_dQ = make_tiled_copy_C(typename Kernel_traits::SmemCopyAtomdQ{}, tiled_mma_dq).get_thread_slice(tidx);
    Tensor taccdQsdQ = smem_thr_copy_dQ.partition_D(sdQ);  // ((Atom,AtomNum),PIPE_M,PIPE_N)

    // Prologue
    if (!Is_first && !Seq_parallel) { __syncthreads(); }

    if (Kernel_traits::V_IN_REGS) {
        copy(gmem_thr_copy_kv, tVgV, tVsV);
        cute::cp_async_fence();
    }

    // copy(gmem_thr_copy_kv, tdOgdO, tdOsdO);
    Tensor tdOrdO = make_fragment_like(tdOgdO);
    Tensor tdOrO = make_fragment_like(tdOgO);
    if (Is_first) {
        // For some reason this calls global load with size=16 instead of 128.
        // copy(gmem_thr_copy_do, tdOgdO, tdOrdO);
        // copy(gmem_thr_copy_do, tdOgO, tdOrO);
        #pragma unroll
        for (int m = 0; m < size<1>(tdOrdO); ++m) {
            copy(gmem_thr_copy_do, tdOgdO(_, m, _), tdOrdO(_, m, _));
            copy(gmem_thr_copy_do, tdOgO(_, m, _), tdOrO(_, m, _));
        }
    } else {
        copy(gmem_thr_copy_do, tdOgdO, tdOsdO);
    }
    copy(gmem_thr_copy_q, tQgQ, tQsQ);

    static_assert(decltype(size<1>(tSrQ))::value == S_MMA_M);
    Tensor lse = make_tensor<ElementAccum>(Shape<Int<2 * S_MMA_M>>{});
    const int warp_id = tidx / 32;
    #pragma unroll
    for (int mi = 0; mi < size(lse) / 2; ++mi) {
        // printf("tidx = %d, row0 = %d, row1 = %d\n", tidx, tidx / 32 * 16 + (tidx % 32) / 4 + 0, tidx / 32 * 16 + (tidx % 32) / 4 + 8);
        lse(mi * 2) = gLSE(mi * (kBlockM / S_MMA_M) + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 0);
        lse(mi * 2 + 1) = gLSE(mi * (kBlockM / S_MMA_M) + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 8);
    }

    // Tensor tKrK = make_fragment_like(tKsK);
    // // copy(gmem_thr_copy_kv, tKgK(_, _, _, 0), tKrK);
    // copy(gmem_thr_copy_kv, tKgK, tKrK);
    // // if (cute::thread(1, 0)) { print(tKrK); }

    // // Copy rmem to smem
    // // copy(tQrQ, tQsQ);
    // cute::cp_async_wait<0>();
    // __syncthreads();
    // // if (cute::thread(1, 0)) { print(tQsQ); }
    // // Tensor sQNoSwizzle = make_tensor(make_smem_ptr(reinterpret_cast<Element *>(smem_)), typename Kernel_traits::SmemLayoutQNoSwizzle{});
    // // if (cute::thread0()) { print(sQNoSwizzle); }

    // // Copy rmem to smem
    // copy(tKrK, tKsK);
    copy(gmem_thr_copy_kv, tKgK, tKsK);
    if (!Kernel_traits::V_IN_REGS) { copy(gmem_thr_copy_kv, tVgV, tVsV); }
    cute::cp_async_fence();

    // if (cute::thread0()) { print(tdOgdO.layout()); printf("\n"); print(tdOrdO); print(tdOrO); }
    if (Is_first) {
        copy(tdOrdO, tdOsdO);
        dot_do_o<Kernel_traits::kGmemThreadsPerRow>(tdOrdO, tdOrO, gdPsum, sdPsum,
                                                    Kernel_traits::kNThreads / (Kernel_traits::kGmemThreadsPerRow), 1.0);
    }

    if (Kernel_traits::V_IN_REGS) {
        cute::cp_async_wait<1>();
        __syncthreads();
        Tensor tdPrV_copy_view = smem_thr_copy_KV.retile_D(tdPrV);
        CUTE_STATIC_ASSERT_V(size<1>(tdPsV) == size<1>(tdPrV_copy_view));            // M
        copy(smem_thr_copy_KV, tdPsV, tdPrV_copy_view);
    }

    int m_block_max = cute::ceil_div(binfo.actual_seqlen_q, kBlockM);

    clear(acc_dv);
    clear(acc_dk);

    // Seems to help a bit even though it says there's more register spilling
    // #pragma unroll 2
    for (int m_block = 0; m_block < m_block_max; ++m_block) {
        Tensor acc_s = partition_fragment_C(tiled_mma_sdp, Shape<Int<kBlockM>, Int<kBlockN>>{});  // (MMA=4, MMA_M, MMA_N)
        // if (cute::thread0()) { print(acc_s); }
        clear(acc_s);
        cute::cp_async_wait<0>();
        __syncthreads();
        // if (cute::thread(0, 0)) { print(sQ); print(sK); }
        // if (cute::thread(1, 0)) { print(tKsK); }

        // Tensor lse = make_tensor<ElementAccum>(Shape<Int<2 * size<1>(acc_s)>>{});
        // #pragma unroll
        // for (int mi = 0; mi < size(lse) / 2; ++mi) {
        //     // printf("tidx = %d, row0 = %d, row1 = %d\n", tidx, tidx / 32 * 16 + (tidx % 32) / 4 + 0, tidx / 32 * 16 + (tidx % 32) / 4 + 8);
        //     // TODO: this might change if each warp takes care of more than 16 rows
        //     lse(mi * 2) = gLSE(mi * 16 + (tidx % 32) / 4 + 0);
        //     lse(mi * 2 + 1) = gLSE(mi * 16 + (tidx % 32) / 4 + 8);
        // }
        // gLSE.data() = gLSE.data() + kBlockM;
        // if (cute::thread0()) { print(lse); }

        Tensor dP_sum = make_fragment_like(lse);
        // TODO: when we change headdim from {32, 64, 128} to 96, this indexing might change
        const int warp_id = tidx / 32;
        // Tensor dP_sum_2 = recast<float2>(dP_sum);
        #pragma unroll
        for (int mi = 0; mi < size(dP_sum) / 2; ++mi) {
            dP_sum(mi * 2) = gdPsum(mi * (kBlockM / S_MMA_M) + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 0);
            dP_sum(mi * 2 + 1) = gdPsum(mi * (kBlockM / S_MMA_M) + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 8);
            // dP_sum(mi * 2) = recast<float>(sdPsum)(mi * (kBlockM / S_MMA_M)  + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 0);
            // dP_sum(mi * 2 + 1) = recast<float>(sdPsum)(mi * (kBlockM / S_MMA_M)  + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 8);
            // dP_sum_2(mi) = sdPsum[mi * (kBlockM / S_MMA_M / 2)  + (warp_id % AtomLayoutMS) * 8 + (tidx % 32) / 4];
        }

        // copy(smem_thr_copy_QdO, tSsQ(_, _, _0{}), tSrQ_copy_view(_, _, _0{}));
        // copy(smem_thr_copy_KV, tSsK(_, _, _0{}), tSrK_copy_view(_, _, _0{}));

        // // if (blockIdx.x == 0 && blockIdx.y == 0 && threadIdx.x <= 4 && m_block == 0 && n_block == 0) { printf("tidx = %d, tSsK.addr = 0x%p\n", tidx, tSsK.data()); }
        // // if (cute::thread(0, 0) && m_block == 0 && n_block == 0) { print(tSsK); }
        // // if (cute::thread(0, 0) && m_block == 0 && n_block == 0) { print(tSrK(_, _, 0)); print(tSrK_copy_view(_, _, 0)); }
        // // __syncthreads();
        // // if (cute::thread(0, 0)) { print(tSsQ); print(tSsK); }
        // // if (cute::thread(0, 0)) { print(tSrQ); print(tSrK); print(acc_s); }
        // // if (cute::thread(0, 0)) { print(tSrQ.layout()); printf("\n"); print(tSrK.layout()); printf("\n"); }

        // #pragma unroll
        // for (int i = 0; i < size<2>(tSrQ); ++i) {
        // // for (int i = 0; i < 1; ++i) {
        //     // if (cute::thread(0, 0)) { print(tSrQ(_, _, i)); print(tSrK(_, _, i)); }
        //     if (i < size<2>(tSrQ) - 1) {
        //         copy(smem_thr_copy_QdO, tSsQ(_, _, i + 1), tSrQ_copy_view(_, _, i + 1));
        //         copy(smem_thr_copy_KV, tSsK(_, _, i + 1), tSrK_copy_view(_, _, i + 1));
        //     }
        //     // if (cute::thread(0, 0)) { print(tSrQ_copy_view(_, _, i)); print(tSrK_copy_view(_, _, i)); }
        //     // __syncthreads();
        //     // if (cute::thread(1, 0)) { print(tSrQ_copy_view(_, _, i)); print(tSrK_copy_view(_, _, i)); }
        //     // __syncthreads();
        //     // if (cute::thread(2, 0)) { print(tSrQ_copy_view(_, _, i)); print(tSrK_copy_view(_, _, i)); }
        //     // __syncthreads();
        //     // if (cute::thread(3, 0)) { print(tSrQ_copy_view(_, _, i)); print(tSrK_copy_view(_, _, i)); }
        //     cute::gemm(tiled_mma_sdp, tSrQ(_, _, i), tSrK(_, _, i), acc_s);
        // }
        flash::gemm(acc_s, tSrQ, tSrK, tSsQ, tSsK, tiled_mma_sdp, smem_thr_copy_QdO, smem_thr_copy_KV);
        // if (cute::thread0()) { print(acc_s); }

        // Reshape acc_s from (MMA=4, MMA_M, MMA_N) to (col=(2, MMA_M), row=(2, MMA_N))
        Tensor scores = make_tensor(acc_s.data(), flash::convert_layout_acc_rowcol(acc_s.layout()));
        // if (cute::thread(0, 0)) { print(scores); }

        // // Copy rmem to smem
        // copy(tVrV, tVsV);

        // Compute the exponential value.
        flash::scale_apply_exp2</*scale_max=*/false>(scores, lse, params.scale_softmax_log2);
        // if (cute::thread(0, 0)) { print(scores); }
        // Convert scores from fp32 to fp16/bf16
        Tensor rP = flash::convert_type<Element>(scores);
        // Reshape rP from (nrow=(2, MMA_M), ncol=(2, MMA_N)) to ((2, 2, 2), MMA_M, MMA_N / 2)
        // if using m16n8k16 or ((2, 2, 1), MMA_M, MMA_N) if using m16n8k8.
        Tensor tPrP = make_tensor(rP.data(), flash::convert_layout_rowcol_Aregs<Kernel_traits::TiledMmaSdP>(rP.layout()));
        // if (cute::thread0() && n_block == 0 && m_block == 0) { print(tPrP); }
        // if (cute::thread0() && n_block == 0 && m_block == 0) { print(tPrP.layout()); printf("\n"); }
        // if (cute::thread0() && n_block == 0 && m_block == 0) { print(tdVrP.layout()); printf("\n"); }
        Tensor tPaP = smem_thr_copy_PdS.retile_S(tPrP);     // ((Atom,AtomNum), MMA_M, MMA_N)
        copy(smem_thr_copy_PdS, tPaP, tPsP);
        // if (cute::thread0()) { print(tPaP); }
        // if (cute::thread0()) { print(sP); }


        Tensor acc_dp = partition_fragment_C(tiled_mma_sdp, Shape<Int<kBlockM>, Int<kBlockN>>{});  // (MMA=4, MMA_M, MMA_N)
        CUTE_STATIC_ASSERT_V(size<0>(acc_dp) == size<0>(acc_s));                     // MMA
        CUTE_STATIC_ASSERT_V(size<1>(acc_dp) == size<1>(acc_s));                     // MMA
        CUTE_STATIC_ASSERT_V(size<2>(acc_dp) == size<2>(acc_s));                     // MMA

        clear(acc_dp);
        // Tensor acc_dp_reshaped = make_tensor(acc_dp.data(), flash::convert_layout_acc_rowcol(acc_dp.layout()));
        // #pragma unroll
        // for (int mi = 0; mi < size<0>(acc_dp_reshaped); ++mi) {
        //     #pragma unroll
        //     for (int ni = 0; ni < size<1>(acc_dp_reshaped); ++ni) {
        //         acc_dp_reshaped(mi, ni) = -dP_sum(mi);
        //     }
        // }

        // if (cute::thread0()) { print(dP_sum); }

        flash::gemm</*A_in_regs=*/false, /*B_in_regs=*/Kernel_traits::V_IN_REGS>(
            acc_dp, tdPrdO, tdPrV, tdPsdO, tdPsV, tiled_mma_sdp, smem_thr_copy_QdO, smem_thr_copy_KV
        );

        // Reshape acc_dp from (MMA=4, MMA_M, MMA_N) to (col=(2, MMA_M), row=(2, MMA_N))
        Tensor dS = make_tensor(acc_dp.data(), scores.layout());
        #pragma unroll
        for (int mi = 0; mi < size<0>(dS); ++mi) {
            #pragma unroll
            for (int ni = 0; ni < size<1>(dS); ++ni) {
                dS(mi, ni) = (dS(mi, ni) - dP_sum(mi)) * scores(mi, ni);
                // dS(mi, ni) = dS(mi, ni) * scores(mi, ni);
            }
        }
        // if (cute::thread0()) { print(dS); }

        Tensor acc_dq = partition_fragment_C(tiled_mma_dq, Shape<Int<kBlockM>, Int<kHeadDim>>{});  // MMA, MMA_M, MMA_K
        tdQgdQaccum.data() = tdQgdQaccum.data() + kBlockM * params.d;
        if (Is_first || Seq_parallel) {
            clear(acc_dq);
        } else {
            // Reshape acc_dq from (4, 1, 2) to (4, 2, 1) to write to gdQaccum
            Tensor acc_dq_reshaped = make_tensor(acc_dq.data(),
                                                 make_layout(get<0>(acc_dq.layout()),
                                                             get<2>(acc_dq.layout()),
                                                             get<1>(acc_dq.layout())));
            copy(gmem_thr_copy_dq_accum, tdQgdQaccum, acc_dq_reshaped);
        }

        if (m_block < m_block_max - 1) {
            // Double buffer for sQ
            const int sQ_offset = m_block % 2 == 0 ? size(sQ) : -size(sQ);
            tQsQ.data() = tQsQ.data() + sQ_offset;
            tSsQ.data() = tSsQ.data() + sQ_offset;
            // Advance gQ
            tQgQ.data() = tQgQ.data() + kBlockM * params.q_row_stride_in_elts;
            copy(gmem_thr_copy_q, tQgQ, tQsQ);
            cute::cp_async_fence();
        }

        Tensor dS_reshaped = make_tensor(dS.data(), acc_dp.layout());
        // Convert dS from fp32 to fp16
        Tensor tdSrdS = flash::convert_type<Element>(dS_reshaped);
        // if (cute::thread0()) { print(tPrP); }
        Tensor tdSadS = smem_thr_copy_PdS.retile_S(tdSrdS);                                          // ((Atom,AtomNum), MMA_M, MMA_N)

        // __syncwarp(); // We need this, not __syncthreads() since the read/write of P is within a warp
        // TODO: actually right now the writing and reading of P are not within a wap.
        // Trying to fix this.
        copy(smem_thr_copy_PdS, tdSadS, tdSsdS);
        __syncthreads(); // Need syncthreads if the tiling for MmaSdP differs from MmadKV

        // Layout p_l = tPrP.layout();
        // Tensor tdVrPt = make_tensor(tPrP.data(), make_layout(get<0>(p_l), get<2>(p_l), get<1>(p_l)));
        // flash::gemm_A_in_regs(acc_dv, tdVrPt, tdVrdO, tdVsdO, tiled_mma_dkv, smem_thr_copy_QdOtransposed);
        // Tensor tdKrdSt = make_tensor(tdSrdS.data(), tdVrPt.layout());
        // flash::gemm_A_in_regs(acc_dk, tdKrdSt, tdKrQ, tdKsQ, tiled_mma_dkv, smem_thr_copy_QdOtransposed);
        flash::gemm(acc_dv, tdVrP, tdVrdO, tdVsP, tdVsdO, tiled_mma_dkv, smem_thr_copy_PdStransposed, smem_thr_copy_QdOtransposed);
        // if (cute::thread0() && n_block == 0 && m_block == 0) { print(tdVrP); }
        // if (cute::thread0()) { print(acc_dv); }

        // __syncwarp(); // We need this, not __syncthreads() since the read/write of dS is within a warp
        __syncthreads(); // Need syncthreads since we're writing to the same sdO location

        if (m_block < m_block_max - 1) {
            // Advance gdO
            tdOgdO.data() = tdOgdO.data() + kBlockM * params.do_row_stride_in_elts;
            if (Is_first) {
                // For some reason this calls global load with size=16 instead of 128.
                // copy(gmem_thr_copy_do, tdOgdO, tdOrdO);
                // copy(gmem_thr_copy_do, tdOgO, tdOrO);
                tdOgO.data() = tdOgO.data() + kBlockM * params.o_row_stride_in_elts;
                #pragma unroll
                for (int m = 0; m < size<1>(tdOrdO); ++m) {
                    copy(gmem_thr_copy_do, tdOgdO(_, m, _), tdOrdO(_, m, _));
                    copy(gmem_thr_copy_do, tdOgO(_, m, _), tdOrO(_, m, _));
                }
            } else {
                copy(gmem_thr_copy_do, tdOgdO, tdOsdO);
                cute::cp_async_fence();
            }
        }

        flash::gemm(acc_dq, tdQrdS, tdQrK, tdQsdS, tdQsK, tiled_mma_dq, smem_thr_copy_dS, smem_thr_copy_Ktransposed);
        // if (cute::thread0()) { print(acc_dq); }

        if (m_block < m_block_max - 1) {
            gLSE.data() = gLSE.data() + kBlockM;
            const int warp_id = tidx / 32;
            #pragma unroll
            for (int mi = 0; mi < size(lse) / 2; ++mi) {
                lse(mi * 2) = gLSE(mi * (kBlockM / S_MMA_M) + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 0);
                lse(mi * 2 + 1) = gLSE(mi * (kBlockM / S_MMA_M) + (warp_id % AtomLayoutMS) * 16 + (tidx % 32) / 4 + 8);
            }
            gdPsum.data() = gdPsum.data() + kBlockM;
            // if (!Is_first && tidx < kBlockM / 2) {
            //     sdPsum(tidx) = recast<float2>(gdPsum)(tidx);
            // if (!Is_first && tidx < kBlockM) {
            //     recast<float>(sdPsum)(tidx) = gdPsum(tidx);
            // }
        }

        if (!Is_last) {
            // Reshape acc_dq from (4, 1, 2) to (4, 2, 1) to write to gdQaccum
            Tensor acc_dq_reshaped = make_tensor(acc_dq.data(),
                                                 make_layout(get<0>(acc_dq.layout()),
                                                             get<2>(acc_dq.layout()),
                                                             get<1>(acc_dq.layout())));
            if (!Seq_parallel) {
                copy(gmem_thr_copy_dq_accum, acc_dq_reshaped, tdQgdQaccum);
                // #pragma unroll
                // for (int m = 0; m < size<1>(tdQgdQaccum); ++m) {
                //     copy(gmem_thr_copy_dq_accum, acc_dq_reshaped(_, m, _), tdQgdQaccum(_, m, _));
                // }
            } else {
                CUTE_STATIC_ASSERT_V(size(acc_dq_reshaped) == size(tdQgdQaccum));
                #pragma unroll
                for (int i = 0; i < size(acc_dq_reshaped); ++i) {
                    atomicAdd(&tdQgdQaccum(i), acc_dq_reshaped(i));
                }
            }
        } else {
            #pragma unroll
            for (int i = 0; i < size(acc_dq); ++i) { acc_dq(i) *= params.scale_softmax; }
            // Convert acc_dq from fp32 to fp16
            Tensor rdQ = flash::convert_type<Element>(acc_dq);
            Tensor taccdQrdQ = smem_thr_copy_dQ.retile_S(rdQ);  // ((Atom,AtomNum), MMA_M, MMA_N)
            copy(smem_thr_copy_dQ, taccdQrdQ, taccdQsdQ);
        }

        flash::gemm(acc_dk, tdKrdS, tdKrQ, tdKsdS, tdKsQ, tiled_mma_dkv, smem_thr_copy_PdStransposed, smem_thr_copy_QdOtransposed);
        // if (cute::thread0()) { print(acc_dk); }
        // Double buffer for sQ
        tdKsQ.data() = tdKsQ.data() + (m_block % 2 == 0 ? size(sQ) : -size(sQ));

        if ((m_block < m_block_max - 1) && Is_first) {
            copy(tdOrdO, tdOsdO);
            dot_do_o<Kernel_traits::kGmemThreadsPerRow>(tdOrdO, tdOrO, gdPsum, sdPsum,
                                                        Kernel_traits::kNThreads / (Kernel_traits::kGmemThreadsPerRow), 1.0);
        }

        if (Is_last) {
            __syncthreads();
            Tensor tdQrdQ = make_tensor<Element>(shape(tdQgdQ));
            copy(gmem_thr_copy_dq, tdQsdQ, tdQrdQ);
            tdQgdQ.data() = tdQgdQ.data() + kBlockM * params.dq_row_stride_in_elts;
            // copy(typename Kernel_traits::CopyAtomdQR2G{}, tdQrdQ, tdQgdQ);
            #pragma unroll
            for (int m = 0; m < size<1>(tdQgdQ); ++m) {
                copy(gmem_thr_copy_dq, tdQrdQ(_, m, _), tdQgdQ(_, m, _));
            }
        }

    }

    // Epilogue

    #pragma unroll
    for (int i = 0; i < size(acc_dk); ++i) { acc_dk(i) *= params.scale_softmax; }

    // Convert acc_dv from fp32 to fp16
    Tensor rdK = flash::convert_type<Element>(acc_dk);
    Tensor rdV = flash::convert_type<Element>(acc_dv);

    Tensor sdK = make_tensor(sK.data(), typename Kernel_traits::SmemLayoutdKV{});              // (SMEM_N, SMEM_K)
    Tensor sdV = make_tensor(sdK.data() + size(sdK), typename Kernel_traits::SmemLayoutdKV{});              // (SMEM_N, SMEM_K)

    // Partition sdV and sdK to match the accumulator partitioning
    auto smem_thr_copy_dKV = make_tiled_copy_C(typename Kernel_traits::SmemCopyAtomdKV{}, tiled_mma_dkv).get_thread_slice(tidx);
    Tensor taccdKrdK = smem_thr_copy_dKV.retile_S(rdK);       // ((Atom,AtomNum), MMA_M, MMA_N)
    Tensor taccdKsdK = smem_thr_copy_dKV.partition_D(sdK);   // ((Atom,AtomNum),PIPE_M,PIPE_N)
    Tensor taccdVrdV = smem_thr_copy_dKV.retile_S(rdV);       // ((Atom,AtomNum), MMA_M, MMA_N)
    Tensor taccdVsdV = smem_thr_copy_dKV.partition_D(sdV);    // ((Atom,AtomNum),PIPE_M,PIPE_N)

    // If we don't need syncthreads here since we writing to the same location as sK and sV.
    // Unless V_IN_REGS.
    if (Kernel_traits::V_IN_REGS && !Is_last) { __syncthreads(); }
    copy(smem_thr_copy_dKV, taccdKrdK, taccdKsdK);
    copy(smem_thr_copy_dKV, taccdVrdV, taccdVsdV);

    // Tensor mdV = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.dv_ptr) + row_offset_dv),
    //                          make_shape(binfo.actual_seqlen_k, Int<kHeadDim>{}),
    //                          make_stride(params.dv_row_stride_in_elts, _1{}));
    // Tensor gdV = local_tile(mdV, Shape<Int<kBlockM>>{}, make_coord(blockIdx.x));  // (kBlockM, kHeadDim)
    const uint32_t row_offset_dk = binfo.k_offset(params.dk_batch_stride_in_elts, params.dk_row_stride_in_elts, bidb)
       + n_block * kBlockN * params.dk_row_stride_in_elts + bidh * params.dk_head_stride_in_elts;
    const uint32_t row_offset_dv = binfo.k_offset(params.dv_batch_stride_in_elts, params.dv_row_stride_in_elts, bidb)
       + n_block * kBlockN * params.dv_row_stride_in_elts + bidh * params.dv_head_stride_in_elts;
    Tensor gdK = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.dk_ptr) + row_offset_dk),
                             Shape<Int<kBlockN>, Int<kHeadDim>>{},
                             make_stride(params.dk_row_stride_in_elts, _1{}));
    Tensor gdV = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.dv_ptr) + row_offset_dv),
                             Shape<Int<kBlockN>, Int<kHeadDim>>{},
                             make_stride(params.dv_row_stride_in_elts, _1{}));

    auto gmem_thr_copy_dKV = typename Kernel_traits::GmemTiledCopydKV{}.get_thread_slice(tidx);
    Tensor tdKsdK = gmem_thr_copy_dKV.partition_S(sdK);   // ((Atom,AtomNum),ATOM_M,ATOM_N)
    Tensor tdKgdK = gmem_thr_copy_dKV.partition_D(gdK);
    Tensor tdVsdV = gmem_thr_copy_dKV.partition_S(sdV);   // ((Atom,AtomNum),ATOM_M,ATOM_N)
    Tensor tdVgdV = gmem_thr_copy_dKV.partition_D(gdV);

    __syncthreads();
    Tensor tdKrdK = make_tensor<Element>(shape(tdKgdK));
    copy(gmem_thr_copy_dKV, tdKsdK, tdKrdK);
    Tensor tdVrdV = make_tensor<Element>(shape(tdVgdV));
    copy(gmem_thr_copy_dKV, tdVsdV, tdVrdV);
    #pragma unroll
    for (int m = 0; m < size<1>(tdKgdK); ++m) {
        copy(gmem_thr_copy_dKV, tdKrdK(_, m, _), tdKgdK(_, m, _));
    }
    #pragma unroll
    for (int m = 0; m < size<1>(tdVgdV); ++m) {
        copy(gmem_thr_copy_dKV, tdVrdV(_, m, _), tdVgdV(_, m, _));
    }

}

////////////////////////////////////////////////////////////////////////////////////////////////////

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, typename Params>
inline __device__ void compute_dq_dk_dv(const Params &params) {

    // The block index for the batch.
    const int bidb = blockIdx.x;
    // const int bidb = blockIdx.y;
    // The block index for the head.
    const int bidh = blockIdx.y;
    // const int bidh = blockIdx.z;
    // The thread index.
    const int tidx = threadIdx.x;

    const int tidx_global = (bidb * params.h + bidh) * blockDim.x * 2 + tidx;
    auto seeds = at::cuda::philox::unpack(params.philox_args);
    Philox ph(std::get<0>(seeds), tidx_global, std::get<1>(seeds));

    const int n_block_max = (params.seqlen_k + Kernel_traits::kBlockN - 1) / Kernel_traits::kBlockN;
    if (n_block_max == 1) {
        compute_dq_dk_dv_1Nblock<Kernel_traits, Is_dropout, Is_causal, true, true>(params, bidb, bidh, ph, 0);
    } else {
        // Iterating backward from n_block_max - 1 to 0 might save 1 register
        compute_dq_dk_dv_1Nblock<Kernel_traits, Is_dropout, Is_causal, true, false>(params, bidb, bidh, ph, n_block_max - 1);
        for (int n_block = n_block_max - 2; n_block > 0; n_block--) {
            compute_dq_dk_dv_1Nblock<Kernel_traits, Is_dropout, Is_causal, false, false>(params, bidb, bidh, ph, n_block);
        }
        compute_dq_dk_dv_1Nblock<Kernel_traits, Is_dropout, Is_causal, false, true>(params, bidb, bidh, ph, 0);
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, typename Params>
inline __device__ void compute_dq_dk_dv_seqparallel(const Params &params) {

    // The block index for the batch.
    const int bidb = blockIdx.y;
    // The block index for the head.
    const int bidh = blockIdx.z;
    // The thread index.
    const int tidx = threadIdx.x;

    const int tidx_global = (bidb * params.h + bidh) * blockDim.x * 2 + tidx;
    auto seeds = at::cuda::philox::unpack(params.philox_args);
    Philox ph(std::get<0>(seeds), tidx_global, std::get<1>(seeds));

    const int n_block = blockIdx.x;
    compute_dq_dk_dv_1Nblock<Kernel_traits, Is_dropout, Is_causal, false, false, /*Seq_parallel=*/true>(
                                                                                                              params, bidb, bidh, ph, n_block
    );
}

////////////////////////////////////////////////////////////////////////////////////////////////////
} // namespace flash
