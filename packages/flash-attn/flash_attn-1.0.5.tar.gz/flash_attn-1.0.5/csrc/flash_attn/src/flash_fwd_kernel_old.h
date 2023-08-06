/******************************************************************************
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
#include "softmax.h"
#include "philox.cuh"

namespace flash {

using namespace cute;

////////////////////////////////////////////////////////////////////////////////////////////////////

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, bool Return_softmax, bool Is_even_M, typename Params, typename Prng>
inline __device__ void compute_attn_1Mblock(const Params &params, const int bidb, const int bidh, Prng &ph) {

    using Element = typename Kernel_traits::Element;
    using ElementAccum = typename Kernel_traits::ElementAccum;

    // Shared memory.
    extern __shared__ char smem_[];

    // The thread index.
    const int tidx = threadIdx.x;

    using X = Underscore;

    constexpr int kBlockM = Kernel_traits::kBlockM;
    constexpr int kBlockN = Kernel_traits::kBlockN;
    constexpr int kHeadDim = Kernel_traits::kHeadDim;

    const BlockInfo binfo(params, bidb);
    // if( binfo.stop_early(loop_step_idx * Cta_tile_p::N) ) return;
    if (blockIdx.x * kBlockM >= binfo.actual_seqlen_q) return;

    const uint32_t row_offset_q = binfo.sum_s_q * params.q_row_stride + bidh * params.q_head_stride;
    const uint32_t row_offset_k = binfo.sum_s_k * params.k_row_stride + bidh * params.k_head_stride;
    const uint32_t row_offset_v = binfo.sum_s_k * params.v_row_stride + bidh * params.v_head_stride;

    // We assume that params.d == kHeadDim for now
    Tensor mQ = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.q_ptr) + row_offset_q),
                            // make_shape(binfo.actual_seqlen_q, params.d),
                            // Need static shape in the k dim here
                            make_shape(binfo.actual_seqlen_q, Int<kHeadDim>{}),
                            make_stride(params.q_row_stride, _1{}));
    // if (cute::thread0()) { print(mQ.layout()); printf("\n"); }
    // Tensor mK = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.k_ptr) + row_offset_k),
    //                         make_shape(binfo.actual_seqlen_k, Int<kHeadDim>{}),
    //                         make_stride(params.k_row_stride, _1{}));

    Tensor gQ = local_tile(mQ, Shape<Int<kBlockM>>{}, make_coord(blockIdx.x));  // (kBlockM, kHeadDim)
    // Tensor gK = local_tile(mK, Shape<Int<kBlockN>, Int<kHeadDim>>{}, make_coord(_, _0{}));  // (kBlockN, kHeadDim, n)
    Tensor gK = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.k_ptr) + row_offset_k),
                            Shape<Int<kBlockN>, Int<kHeadDim>>{}, make_stride(params.k_row_stride, _1{}));
    Tensor gV = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.v_ptr) + row_offset_v),
                            Shape<Int<kBlockN>, Int<kHeadDim>>{}, make_stride(params.v_row_stride, _1{}));

    Tensor sQ = make_tensor(make_smem_ptr(reinterpret_cast<Element *>(smem_)),
                            typename Kernel_traits::SmemLayoutQ{});
    // Careful we're using the same smem for sQ and sK | sV if Is_Q_in_regs
    Tensor sK = make_tensor(sQ.data() + (Kernel_traits::Is_Q_in_regs ? 0 : size(sQ)),
                            typename Kernel_traits::SmemLayoutKV{});
    Tensor sV = make_tensor(sK.data() + size(sK), typename Kernel_traits::SmemLayoutKV{});
    Tensor sVtransposed = make_tensor(sV.data(), typename Kernel_traits::SmemLayoutVtransposed{});
    Tensor sVtransposedNoSwizzle = make_tensor(sV.data(),
                                               typename Kernel_traits::SmemLayoutVtransposedNoSwizzle{});

    auto gmem_thr_copy_Q = typename Kernel_traits::GmemTiledCopyQ{}.get_thread_slice(tidx);
    auto gmem_thr_copy_KV = typename Kernel_traits::GmemTiledCopyKV{}.get_thread_slice(tidx);
    Tensor tQgQ = gmem_thr_copy_Q.partition_S(gQ);
    Tensor tQsQ = gmem_thr_copy_Q.partition_D(sQ);
    Tensor tKgK = gmem_thr_copy_KV.partition_S(gK);  // (KCPY, KCPY_N, KCPY_K)
    Tensor tKsK = gmem_thr_copy_KV.partition_D(sK);
    Tensor tVgV = gmem_thr_copy_KV.partition_S(gV);  // (VCPY, VCPY_N, VCPY_K)
    Tensor tVsV = gmem_thr_copy_KV.partition_D(sV);

    typename Kernel_traits::TiledMma tiled_mma;
    auto thr_mma = tiled_mma.get_thread_slice(tidx);
    Tensor tSrQ  = thr_mma.partition_fragment_A(sQ);                           // (MMA,MMA_M,MMA_K)
    Tensor tSrK  = thr_mma.partition_fragment_B(sK);                           // (MMA,MMA_N,MMA_K)
    CUTE_STATIC_ASSERT_V(size<2>(tSrQ) == size<2>(tSrK));                      // MMA_K

    Tensor acc_o = partition_fragment_C(tiled_mma, Shape<Int<kBlockM>, Int<kHeadDim>>{});  // MMA, MMA_M, MMA_K
    // Tensor tOrV  = thr_mma.partition_fragment_B(sVtransposed);                           // (MMA, MMA_K,MMA_N)
    Tensor tOrV  = thr_mma.partition_fragment_B(sVtransposedNoSwizzle);                           // (MMA, MMA_K,MMA_N)
    CUTE_STATIC_ASSERT_V(size<1>(tOrV) == size<2>(acc_o));                     // MMA_N

    //
    // Copy Atom retiling
    //

    auto smem_thr_copy_Q = make_tiled_copy_A(typename Kernel_traits::SmemCopyAtom{}, tiled_mma).get_thread_slice(tidx);
    Tensor tSsQ = smem_thr_copy_Q.partition_S(sQ);
    Tensor tSrQ_copy_view = smem_thr_copy_Q.retile_D(tSrQ);
    CUTE_STATIC_ASSERT_V(size<1>(tSsQ) == size<1>(tSrQ_copy_view));            // M

    auto smem_thr_copy_K = make_tiled_copy_B(typename Kernel_traits::SmemCopyAtom{}, tiled_mma).get_thread_slice(tidx);
    Tensor tSsK = smem_thr_copy_K.partition_S(sK);
    Tensor tSrK_copy_view = smem_thr_copy_K.retile_D(tSrK);
    CUTE_STATIC_ASSERT_V(size<1>(tSsK) == size<1>(tSrK_copy_view));            // N

    auto smem_thr_copy_V = make_tiled_copy_B(typename Kernel_traits::SmemCopyAtomTransposed{}, tiled_mma).get_thread_slice(tidx);
    Tensor tOsV = smem_thr_copy_V.partition_S(sVtransposed);
    Tensor tOrV_copy_view = smem_thr_copy_V.retile_D(tOrV);
    CUTE_STATIC_ASSERT_V(size<1>(tOsV) == size<1>(tOrV_copy_view));            // N

    // TODO: this might need to change if we change the mma instruction in SM70
    Tensor scores_max = make_tensor<ElementAccum>(Shape<Int<2 * size<1>(acc_o)>>{});
    Tensor scores_sum = make_fragment_like(scores_max);

    //
    // PREDICATES
    //

    // // Allocate predicate tensors for m and n
    // Tensor tQpQ = make_tensor<bool>(make_shape(size<1>(tQsQ), size<2>(tQsQ)), Stride<_1,_0>{});
    // Tensor tKVpKV = make_tensor<bool>(make_shape(size<1>(tKsK), size<2>(tKsK)), Stride<_1,_0>{});

    // Construct identity layout for sQ and sK
    Tensor cQ = make_identity_tensor(make_shape(size<0>(sQ), size<1>(sQ)));    // (BLK_M,BLK_K) -> (blk_m,blk_k)
    Tensor cKV = make_identity_tensor(make_shape(size<0>(sK), size<1>(sK)));    // (BLK_N,BLK_K) -> (blk_n,blk_k)

    // Repeat the partitioning with identity layouts
    Tensor tQcQ = gmem_thr_copy_Q.partition_S(cQ);                             // (ACPY,ACPY_M,ACPY_K) -> (blk_m,blk_k)
    Tensor tKVcKV = gmem_thr_copy_KV.partition_S(cKV);                             // (BCPY,BCPY_N,BCPY_K) -> (blk_n,blk_k)

    // // Set predicates for m bounds
    // CUTLASS_PRAGMA_UNROLL
    // for (int m = 0; m < size<0>(tQpQ); ++m) {
    //     // if (cute::thread0()) {printf("m = %d\n", get<0>(tQcQ(0, m, 0))); }
    //     tQpQ(m, 0) = get<0>(tQcQ(0, m, 0)) < binfo.actual_seqlen_q - blockIdx.x * kBlockM;  // blk_m coord < residue_m
    // }
    // // if (cute::thread0()) { print(tQpQ); }
    // // Set predicates for n bounds
    // CUTLASS_PRAGMA_UNROLL
    // for (int n = 0; n < size<0>(tKVpKV); ++n) {
    //     tKVpKV(n, 0) = get<0>(tKVcKV(0, n, 0)) < binfo.actual_seqlen_k;  // blk_n coord < residue_n
    // }

    // Prologue

    Tensor tQrQ = make_fragment_like(tQgQ);
    // copy(gmem_thr_copy_Q, tQgQ, tQsQ);
    // We don't need to clear the sQ smem tiles since we'll only write out the valid outputs
    // copy_if(gmem_thr_copy_Q, tQpQ, tQgQ, tQsQ);
    #pragma unroll
    for (int m = 0; m < size<1>(tQgQ); ++m) {
        if (get<0>(tQcQ(0, m, 0)) < binfo.actual_seqlen_q - blockIdx.x * kBlockM) {
            copy(gmem_thr_copy_Q, tQgQ(_, m, _), tQsQ(_, m, _));
        }
    }

    // // Copy rmem to smem
    // // copy(tQrQ, tQsQ);
    // cute::cp_async_wait<0>();
    // __syncthreads();
    // // if (cute::thread(1, 0)) { print(tQsQ); }
    // // Tensor sQNoSwizzle = make_tensor(make_smem_ptr(reinterpret_cast<Element *>(smem_)), typename Kernel_traits::SmemLayoutQNoSwizzle{});
    // // if (cute::thread0()) { print(sQNoSwizzle); }

    if (Kernel_traits::Is_Q_in_regs) {
        cute::cp_async_wait<0>();
        __syncthreads();
        copy(smem_thr_copy_Q, tSsQ, tSrQ_copy_view);
        __syncthreads();
    }

    uint32_t n_block_max = cute::ceil_div(binfo.actual_seqlen_k, kBlockN);
    if (Is_causal) {
        n_block_max = std::min(n_block_max, cute::ceil_div(blockIdx.x * kBlockM, kBlockN) + 1);
        // if (threadIdx.x == 0 && blockIdx.y == 0 && blockIdx.z == 0) {
        //     printf("blockIdx.x = %d, n_block_max = %d\n", blockIdx.x, n_block_max);
        // }
    }

    // // Copy rmem to smem
    Tensor tKrK = make_fragment_like(tKsK);
    // copy(gmem_thr_copy_KV, tKgK, tKrK);
    // copy(tKrK, tKsK);
    if (Is_even_M || n_block_max > 1) {
        copy(gmem_thr_copy_KV, tKgK, tKsK);
    } else {
        // We don't need to clear the sK smem tiles since we'll mask out the scores anyway.
        // copy_if(gmem_thr_copy_KV, tKVpKV, tKgK, tKsK);
        #pragma unroll
        for (int n = 0; n < size<1>(tKgK); ++n) {
            if (get<0>(tKVcKV(0, n, 0)) < binfo.actual_seqlen_k) {
                copy(gmem_thr_copy_KV, tKgK(_, n, _), tKsK(_, n, _));
            }
        }
    }
    cute::cp_async_fence();
    // Advance gK
    tKgK.data() = tKgK.data() + kBlockN * params.k_row_stride;

    clear(acc_o);

    auto seeds = at::cuda::philox::unpack(params.philox_args);
    unsigned long long seed = std::get<0>(seeds);
    unsigned long long offset = std::get<1>(seeds) + (bidb * params.h + bidh) * 32 + tidx % 32;
    // Unrolling seems to help even though it says there's more register spilling
    #pragma unroll 2
    for (uint32_t n_block = 0; n_block < n_block_max; ++n_block) {
        Tensor acc_s = partition_fragment_C(tiled_mma, Shape<Int<kBlockM>, Int<kBlockN>>{});  // (MMA=4, MMA_M, MMA_N)
        // if (cute::thread0()) { print(acc_s.layout()); printf("\n"); }
        CUTE_STATIC_ASSERT_V(size<1>(tSrQ) == size<1>(acc_s));                     // MMA_M
        CUTE_STATIC_ASSERT_V(size<1>(tSrK) == size<2>(acc_s));                     // MMA_N

        clear(acc_s);
        cute::cp_async_wait<0>();
        __syncthreads();

        Tensor tVrV = make_fragment_like(tVsV);
        // copy(gmem_thr_copy_KV, tVgV, tVrV);
        if (Is_even_M || n_block < n_block_max - 1) {
            copy(gmem_thr_copy_KV, tVgV, tVsV);
        } else {
            // Clear the smem tiles to account for predicated off loads
            // clear(tVsV);
            // copy_if(gmem_thr_copy_KV, tKVpKV, tVgV, tVsV);
            #pragma unroll
            for (int n = 0; n < size<1>(tVgV); ++n) {
                if (get<0>(tKVcKV(0, n, 0)) < binfo.actual_seqlen_k - n_block * kBlockN) {
                    copy(gmem_thr_copy_KV, tVgV(_, n, _), tVsV(_, n, _));
                } else {
                    clear(tVsV(_, n, _));
                }
            }
        }
        cute::cp_async_fence();
        // Advance gV
        tVgV.data() = tVgV.data() + kBlockN * params.v_row_stride;

        if (!Kernel_traits::Is_Q_in_regs) {
            copy(smem_thr_copy_Q, tSsQ(_, _, _0{}), tSrQ_copy_view(_, _, _0{}));
        }
        copy(smem_thr_copy_K, tSsK(_, _, _0{}), tSrK_copy_view(_, _, _0{}));
        #pragma unroll
        for (int i = 0; i < size<2>(tSrQ); ++i) {
            if (i < size<2>(tSrQ) - 1) {
                if (!Kernel_traits::Is_Q_in_regs) {
                    copy(smem_thr_copy_Q, tSsQ(_, _, i + 1), tSrQ_copy_view(_, _, i + 1));
                }
                copy(smem_thr_copy_K, tSsK(_, _, i + 1), tSrK_copy_view(_, _, i + 1));
            }
            cute::gemm(tiled_mma, tSrQ(_, _, i), tSrK(_, _, i), acc_s);
        }

        // if (cute::thread0() && n_block == 0) { print(acc_s.layout()); printf("\n"); }
        // if (cute::thread0() && n_block == 0) { print(acc_s); }

        // Reshape acc_s from (MMA=4, MMA_M, MMA_N) to (nrow=(2, MMA_M), ncol=(2, MMA_N))
        Layout s_l = logical_divide(acc_s.layout(), Shape<_2>{});  // ((2, 2), MMA_M, MMA_N)
        Tensor scores = make_tensor(acc_s.data(),
                                    make_layout(make_layout(get<0, 1>(s_l), get<1>(s_l)),
                                                make_layout(get<0, 0>(s_l), get<2>(s_l))));
        // if (cute::thread(0, 0)) { print(scores); }
        if (!Is_causal) {
            if (!Is_even_M && n_block == n_block_max - 1) {
                flash::apply_mask(scores, binfo.actual_seqlen_k - n_block * kBlockN);
            }
        } else {
            if (n_block >= n_block_max - cute::ceil_div(kBlockM, kBlockN)) {
                flash::apply_mask_causal(scores, n_block * kBlockN, binfo.actual_seqlen_k,
                                         blockIdx.x * kBlockM);
            }
        }
        // if (cute::thread0()) { print(scores); }

        // // Copy rmem to smem
        // copy(tVrV, tVsV);

        if (n_block == 0) {
            flash::template reduce_max</*zero_init=*/true>(scores, scores_max);
        } else {
            Tensor scores_max_prev = make_fragment_like(scores_max);
            copy(scores_max, scores_max_prev);
            flash::template reduce_max</*zero_init=*/false>(scores, scores_max);
            // Reshape acc_o from (MMA=4, MMA_M, MMA_K) to (nrow=(2, MMA_M), ncol=(2, MMA_K))
            Layout o_l = logical_divide(acc_o.layout(), Shape<_2>{});  // ((2, 2), MMA_M, MMA_N)
            Tensor acc_o_reshaped = make_tensor(acc_o.data(),
                                                make_layout(make_layout(get<0, 1>(o_l), get<1>(o_l)),
                                                            make_layout(get<0, 0>(o_l), get<2>(o_l))));
            #pragma unroll
            for (int mi = 0; mi < size(scores_max); ++mi) {
                // TODO: we might need to deal with scores_max == -inf here?
                float scores_scale = exp2f((scores_max_prev(mi) - scores_max(mi)) * params.scale_softmax_log2);
                scores_sum(mi) *= scores_scale;
                #pragma unroll
                for (int ni = 0; ni < size<1>(acc_o_reshaped); ++ni) {
                    acc_o_reshaped(mi, ni) *= scores_scale;
                }
            }
            // if (cute::thread(0, 0)) { print(scores_max_prev); print(scores_sum); }
        }
        // if (cute::thread(0, 0)) { print(scores_max); }

        // Compute the exponential value.
        // flash::scale_apply_exp(scores, scores_max, params.scale_softmax);
        flash::scale_apply_exp2(scores, scores_max, params.scale_softmax_log2);
        // if (cute::thread(1, 0)) { print(scores); }

        Tensor scores_sum_prev = make_fragment_like(scores_sum);
        if (n_block == 0) {
            flash::reduce_sum(scores, scores_sum);
        } else {
            copy(scores_sum, scores_sum_prev);
            flash::reduce_sum(scores, scores_sum);
            #pragma unroll
            for (int mi = 0; mi < size(scores_sum); ++mi) {
                scores_sum(mi) += scores_sum_prev(mi);
            }
        }

        // if (cute::thread(0, 0)) { print(scores_sum); }

        // if (Is_dropout) {
        //     flash::apply_dropout(scores, ph, params.p_dropout_in_uint8_t);
        // }

        // Convert acc_s from fp32 to fp16/bf16
        cutlass::NumericArrayConverter<Element, ElementAccum, size(scores)> convert_p;
        auto frag_p = convert_p(*reinterpret_cast<const cutlass::Array<float, size(scores)>*>(scores.data()));
        Tensor rP = make_tensor(make_rmem_ptr<Element>(&frag_p), scores.layout());
        // if (cute::thread(1, 0)) { print(rP); }
        // Reshape rP from (nrow=(2, MMA_M), ncol=(2, MMA_N)) to ((2, 2, 2), MMA_M, MMA_N / 2) if using m16n8k16
        // Reshape rP from (nrow=(2, MMA_M), ncol=(2, MMA_N)) to ((2, 2), MMA_M, MMA_N) if using m16n8k8
        using MMA_N_divisor = typename std::conditional<std::is_same<typename Kernel_traits::TiledMma::Shape_MNK, Shape<_16, _8, _8>>::value,
            _1, _2>::type;
        // Layout p_l = logical_divide(rP.layout(), Shape<X, Shape<X, _2>>{});  // ((2, MMA_M), (2, (2, MMA_N / 2)))
        Layout p_l = logical_divide(rP.layout(), Shape<X, Shape<X, MMA_N_divisor>>{});  // ((2, MMA_M), (2, (2, MMA_N / 2)))
        Tensor tOrP = make_tensor(rP.data(),
                                  make_layout(make_layout(get<1, 0>(p_l), get<0, 0>(p_l), get<1, 1, 0>(p_l)),
                                              get<0, 1>(p_l),
                                              get<1, 1, 1>(p_l)));
        CUTE_STATIC_ASSERT_V(size<1>(tOrP) == size<1>(acc_o));                     // MMA_M
        CUTE_STATIC_ASSERT_V(size<2>(tOrP) == size<2>(tOrV));                     // MMA_K

        if (Is_dropout) {
            // if (cute::thread0()) {print(tOrP);}
            // flash::apply_dropout(tOrP, ph, params.p_dropout_in_uint8_t);
            // flash::apply_dropout(tOrP, ph, params.p_dropout_in_uint16_t);
            auto seeds = at::cuda::philox::unpack(params.philox_args);
            // TODO: we might switch from 16x32 block to 32x16 block.
            uint32_t warp_id = tidx / 32;
            uint32_t block_row_idx = (blockIdx.x * Kernel_traits::kNWarps + warp_id) * (kBlockM / Kernel_traits::kNWarps / 16);
            uint32_t block_col_idx = n_block * kBlockN / 32;
            uint32_t num_block_cols = cute::ceil_div(binfo.actual_seqlen_k, 32);
            uint32_t subsequence_start = block_row_idx * num_block_cols + block_col_idx;
            flash::apply_dropout_philox(tOrP, params.p_dropout_in_uint8_t,
                                        seed, offset, subsequence_start, num_block_cols);
            // if (cute::thread0()) {print(tOrP);}
        }
        // if (cute::thread0() && n_block == 0) { print(tOrP.layout()); printf("\n"); }

        cute::cp_async_wait<0>();
        __syncthreads();
        // if (cute::thread(0, 0)) { print(sV); }
        // if (cute::thread(0, 0)) { print(tVsV); }
        // Tensor sVNoSwizzle = make_tensor(make_smem_ptr(reinterpret_cast<Element *>(smem_) + 128 * 64 + 64 * 64), typename Kernel_traits::SmemLayoutVNoSwizzle{});
        // if (cute::thread0()) { print(sVNoSwizzle); }

        if (n_block < n_block_max - 1) {
            // copy(gmem_thr_copy_KV, tKgK, tKrK);
            if (Is_even_M || n_block + 1 < n_block_max - 1) {
                copy(gmem_thr_copy_KV, tKgK, tKsK);
            } else {
                // Set predicates for n bounds
                // CUTLASS_PRAGMA_UNROLL
                // for (int n = 0; n < size<0>(tKVpKV); ++n) {
                //     tKVpKV(n, 0) = get<0>(tKVcKV(0, n, 0)) < binfo.actual_seqlen_k - (n_block + 1) * kBlockN;  // blk_n coord < residue_n
                // }
                // copy_if(gmem_thr_copy_KV, tKVpKV, tKgK, tKsK);
                #pragma unroll
                for (int n = 0; n < size<1>(tKgK); ++n) {
                    if (get<0>(tKVcKV(0, n, 0)) < binfo.actual_seqlen_k - (n_block + 1) * kBlockN) {
                        copy(gmem_thr_copy_KV, tKgK(_, n, _), tKsK(_, n, _));
                    }
                }
            }
            cute::cp_async_fence();
            // Advance gK
            tKgK.data() = tKgK.data() + kBlockN * params.k_row_stride;
        }

        copy(smem_thr_copy_V, tOsV(_, _, _0{}), tOrV_copy_view(_, _, _0{}));
        #pragma unroll
        for (int i = 0; i < size<2>(tOrP); ++i) {
            if (i < size<2>(tOrP) - 1) { copy(smem_thr_copy_V, tOsV(_, _, i + 1), tOrV_copy_view(_, _, i + 1)); }
            cute::gemm(tiled_mma, tOrP(_, _, i), tOrV(_, _, i), acc_o);
        }

        // if (cute::thread0()) { print(acc_o); }
        // // Copy rmem to smem
        // if (n_block < n_block_max - 1) {
        //     copy(tKrK, tKsK);
        // }

    }

    // Epilogue

    // Reshape acc_o from (MMA=4, MMA_M, MMA_K) to (nrow=(2, MMA_M), ncol=(2, MMA_K))
    Layout o_l = logical_divide(acc_o.layout(), Shape<_2>{});  // ((2, 2), MMA_M, MMA_N)
    Tensor acc_o_reshaped = make_tensor(acc_o.data(),
                                        make_layout(make_layout(get<0, 1>(o_l), get<1>(o_l)),
                                                    make_layout(get<0, 0>(o_l), get<2>(o_l))));
    Tensor lse = make_fragment_like(scores_sum);
    #pragma unroll
    for (int mi = 0; mi < size<0>(acc_o_reshaped); ++mi) {
        float sum = scores_sum(mi);
        float inv_sum = (sum == 0.f || sum != sum) ? 1.f : 1.f / sum;
        lse(mi) = (sum == 0.f || sum != sum) ? INFINITY : scores_max(mi) * params.scale_softmax + __logf(sum);
        #pragma unroll
        for (int ni = 0; ni < size<1>(acc_o_reshaped); ++ni) {
            acc_o_reshaped(mi, ni) *= inv_sum;
        }
    }

    // if (cute::thread0()) { print(acc_o_reshaped); }

    // Convert acc_o from fp32 to fp16/bf16
    cutlass::NumericArrayConverter<Element, ElementAccum, size(acc_o)> convert_o;
    auto frag_o = convert_o(*reinterpret_cast<const cutlass::Array<float, size(acc_o)>*>(acc_o.data()));
    Tensor rO = make_tensor(make_rmem_ptr<Element>(&frag_o), acc_o.layout());

    Tensor sO = make_tensor(sQ.data(), typename Kernel_traits::SmemLayoutO{});    // (SMEM_M,SMEM_N)
    // Partition sO to match the accumulator partitioning
    auto smem_thr_copy_O = make_tiled_copy_C(typename Kernel_traits::SmemCopyAtomO{}, tiled_mma).get_thread_slice(tidx);
    Tensor taccOrO = smem_thr_copy_O.retile_S(rO);        // ((Atom,AtomNum), MMA_M, MMA_N)
    Tensor taccOsO = smem_thr_copy_O.partition_D(sO);     // ((Atom,AtomNum),PIPE_M,PIPE_N)

    // sO has the same size as sQ, so we don't need to sync here.
    if (Kernel_traits::Is_Q_in_regs) { __syncthreads(); }

    copy(smem_thr_copy_O, taccOrO, taccOsO);

    const uint32_t row_offset_o = binfo.sum_s_q * params.o_row_stride + bidh * params.o_head_stride;
    const uint32_t row_offset_lse = (bidb * params.h + bidh) * params.seqlen_q;
    Tensor mO = make_tensor(make_gmem_ptr(reinterpret_cast<Element *>(params.o_ptr) + row_offset_o),
                            make_shape(binfo.actual_seqlen_q, Int<kHeadDim>{}),
                            make_stride(params.o_row_stride, _1{}));
    Tensor gO = local_tile(mO, Shape<Int<kBlockM>>{}, make_coord(blockIdx.x));  // (kBlockM, kHeadDim)
    Tensor mLSE = make_tensor(make_gmem_ptr(reinterpret_cast<ElementAccum *>(params.softmax_lse_ptr) + row_offset_lse),
                              make_shape(binfo.actual_seqlen_q), Stride<_1>{});
    Tensor gLSE = local_tile(mLSE, Shape<Int<kBlockM>>{}, make_coord(blockIdx.x));  // (kBlockM)

    auto gmem_thr_copy_O = typename Kernel_traits::GmemTiledCopyO{}.get_thread_slice(tidx);
    Tensor tOsO = gmem_thr_copy_O.partition_S(sO);                                   //               ((Atom,AtomNum),ATOM_M,ATOM_N)
    Tensor tOgO = gmem_thr_copy_O.partition_D(gO);

    // Tensor cO = local_tile(make_identity_tensor(make_shape(size<0>(mO), size<1>(mO))),
    //                        Shape<Int<kBlockM>>{}, make_coord(blockIdx.x));
    // Tensor tOcQ  = thr_mma.partition_fragment_A(cO);                           // (MMA,MMA_M,MMA_K)
    // if (cute::thread0()) { print(tOcQ); }
    // if (cute::thread0()) { print(lse); }
    __syncthreads();

    Tensor tOrO = make_tensor<Element>(shape(tOgO));
    copy(gmem_thr_copy_O, tOsO, tOrO);

    static_assert(decltype(size(lse))::value % 2 == 0);
    if (tidx % 4 == 0) {
        #pragma unroll
        for (int mi = 0; mi < size(lse) / 2; ++mi) {
            // printf("tidx = %d, row0 = %d, row1 = %d\n", tidx, tidx / 32 * 16 + (tidx % 32) / 4 + 0, tidx / 32 * 16 + (tidx % 32) / 4 + 8);
            const uint32_t row0 = (mi * Kernel_traits::kNWarps + tidx / 32) * 16 + (tidx % 32) / 4 + 0;
            const uint32_t row1 = (mi * Kernel_traits::kNWarps + tidx / 32) * 16 + (tidx % 32) / 4 + 8;
            if (row0 < binfo.actual_seqlen_q - blockIdx.x * kBlockM) { gLSE(row0) = lse(mi * 2); }
            if (row1 < binfo.actual_seqlen_q - blockIdx.x * kBlockM) { gLSE(row1) = lse(mi * 2 + 1); }
        }
    }

    // Construct identity layout for sO and sK
    Tensor cO = make_identity_tensor(make_shape(size<0>(sO), size<1>(sO)));    // (BLK_M,BLK_K) -> (blk_m,blk_k)
    // Repeat the partitioning with identity layouts
    Tensor tOcO = gmem_thr_copy_O.partition_D(cO);                             // (ACPY,ACPY_M,ACPY_K) -> (blk_m,blk_k)
    // For some reason this calls global store with size=16 (instead of 128) so it's much slower.
    // By calling copy on each slice indexed by m, it calls global store with size=128.
    // copy(gmem_thr_copy_O, tOrO, tOgO);
    #pragma unroll
    for (int m = 0; m < size<1>(tOgO); ++m) {
        // if (cute::thread0()) {printf("m = %d\n", get<0>(tQcQ(0, m, 0))); }
        if (get<0>(tOcO(0, m, 0)) < binfo.actual_seqlen_q - blockIdx.x * kBlockM) {
            copy(gmem_thr_copy_O, tOrO(_, m, _), tOgO(_, m, _));
        }
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, bool Return_softmax, bool Is_even_M, typename Params>
inline __device__ void compute_attn(const Params &params) {
    // The block index for the batch.
    // const int bidb = blockIdx.x;
    const int bidb = blockIdx.y;
    // The block index for the head.
    // const int bidh = blockIdx.y;
    const int bidh = blockIdx.z;
    // The thread index.
    const int tidx = threadIdx.x;

    // We want the fwd and bwd to generate the same dropout pattern (RNG), without restricting
    // them to have the same number of threads or have to traverse the attention matrix
    // in the same order.
    // In the Philox RNG, we use the offset to store the batch, head, and the lane id
    // (within a warp). We use the subsequence to store the location of the 16 x 16 blocks within
    // the attention matrix. This way, as long as we have the batch, head, and the location of
    // the 16 x 16 block within the attention matrix, we can generate the exact same dropout pattern.
    auto seeds = at::cuda::philox::unpack(params.philox_args);
    Philox ph(std::get<0>(seeds), 0, std::get<1>(seeds) + (bidb * params.h + bidh) * 32 + tidx % 32);

    flash::compute_attn_1Mblock<Kernel_traits, Is_dropout, Is_causal, Return_softmax, Is_even_M>(params, bidb, bidh, ph);
}

////////////////////////////////////////////////////////////////////////////////////////////////////

} // namespace flash