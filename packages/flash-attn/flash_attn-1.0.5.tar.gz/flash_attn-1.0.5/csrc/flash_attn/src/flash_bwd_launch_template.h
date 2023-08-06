// Copyright (c) 2023, Tri Dao.

#pragma once

#include "static_switch.h"
#include "flash.h"
#include "flash_bwd_kernel.h"

template<bool Clear_dQaccum=true, typename Kernel_traits>
__global__ void flash_bwd_dot_do_o_kernel(Flash_bwd_params params) {
    flash::compute_dot_do_o<Clear_dQaccum, Kernel_traits>(params);
}

template<typename Kernel_traits>
__global__ void flash_bwd_clear_dkvaccum_kernel(Flash_bwd_params params) {
    flash::clear_dKVaccum<Kernel_traits>(params);
}

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, bool Is_even_M, bool Is_even_K>
__global__ void flash_bwd_dq_dk_dv_loop_kernel(Flash_bwd_params params) {
    flash::compute_dq_dk_dv<Kernel_traits, Is_dropout, Is_causal, Is_even_M, Is_even_K>(params);
}

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, bool Is_even_M, bool Is_even_K>
__global__ void flash_bwd_dq_dk_dv_loop_seqq_parallel_kernel(Flash_bwd_params params) {
    flash::compute_dq_dk_dv_seqq_parallel<Kernel_traits, Is_dropout, Is_causal, Is_even_M, Is_even_K>(params);
}

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, bool Is_even_N, bool Is_even_K>
__global__ void flash_bwd_dq_dk_dv_loop_seqk_parallel_kernel(Flash_bwd_params params) {
    flash::compute_dq_dk_dv_seqk_parallel<Kernel_traits, Is_dropout, Is_causal, Is_even_N, Is_even_K>(params);
}

template<typename Kernel_traits>
__global__ void flash_bwd_convert_dq_kernel(Flash_bwd_params params) {
    flash::convert_dQ<Kernel_traits>(params);
}

template<typename Kernel_traits>
__global__ void flash_bwd_convert_dkv_kernel(Flash_bwd_params params) {
    flash::convert_dKV<Kernel_traits>(params);
}

template<typename Kernel_traits>
void run_flash_bwd_loop(Flash_bwd_params &params, cudaStream_t stream, const bool configure) {
    /* bool is_dropout = params.p_dropout < 1.f;  // params.p_dropout is the probability of "keeping" */
    /* // Work-around for gcc 7. It doesn't like nested BOOL_SWITCH. */
    /* BOOL_SWITCH(is_dropout, IsDropoutConst, [&] { */
    /*     auto kernel = params.is_causal */
    /*         ? &flash_bwd_dq_dk_dv_loop_kernel<Kernel_traits, IsDropoutConst, true> */
    /*         : &flash_bwd_dq_dk_dv_loop_kernel<Kernel_traits, IsDropoutConst, false>; */
    /*     if (params.seqlen_k == blocksize_c) { */
    /*         kernel = params.is_causal */
    /*             ? &flash_bwd_dq_dk_dv_loop_kernel<Kernel_traits, IsDropoutConst, true, /\*loop_steps=*\/1> */
    /*             : &flash_bwd_dq_dk_dv_loop_kernel<Kernel_traits, IsDropoutConst, false, /\*loop_steps=*\/1>; */
    /*     } else if (params.seqlen_k == blocksize_c * 2) { */
    /*         kernel = params.is_causal */
    /*             ? &flash_bwd_dq_dk_dv_loop_kernel<Kernel_traits, IsDropoutConst, true, /\*loop_steps=*\/2> */
    /*             : &flash_bwd_dq_dk_dv_loop_kernel<Kernel_traits, IsDropoutConst, false, /\*loop_steps=*\/2>; */
    /*     } */
    /*     /\* auto kernel_seqparallel = params.is_causal *\/ */
    /*     /\*     ? &flash_bwd_q_dk_dv_loop_seqparallel_kernel<Kernel_traits, IsDropoutConst, true> *\/ */
    /*     /\*     : &flash_bwd_q_dk_dv_loop_seqparallel_kernel<Kernel_traits, IsDropoutConst, false>; *\/ */
    /*     if( smem_size_dq_dk_dv >= 48 * 1024 ) { */
    /*         C10_CUDA_CHECK(cudaFuncSetAttribute( */
    /*             kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, smem_size_dq_dk_dv)); */
    /*         /\* C10_CUDA_CHECK(cudaFuncSetAttribute( *\/ */
    /*         /\*     kernel_seqparallel, cudaFuncAttributeMaxDynamicSharedMemorySize, smem_size_dq_dk_dv)); *\/ */
    /*     } */
    /*     /\* // Automatically set num_splits to maximize occupancy *\/ */
    /*     /\* if (params.num_splits <= 0) { *\/ */
    /*     /\*     int ctas_per_sm; *\/ */
    /*     /\*     cudaError status_ = cudaOccupancyMaxActiveBlocksPerMultiprocessor( *\/ */
    /*     /\*         &ctas_per_sm, kernel, Kernel_traits::THREADS, smem_size_dq_dk_dv); *\/ */
    /*     /\*     auto dprops = at::cuda::getCurrentDeviceProperties(); *\/ */
    /*     /\*     // printf("CTAS_PER_SM = %d, nSMs = %d\n", ctas_per_sm, dprops->multiProcessorCount); *\/ */
    /*     /\*     constexpr int M = Kernel_traits::Cta_tile_p::M; *\/ */
    /*     /\*     // We don't want more than 10 splits due to numerical error. *\/ */
    /*     /\*     // Numerical error on dk/dv scales as sqrt(num_splits). *\/ */
    /*     /\*     params.num_splits = num_splits_heuristic_bwd( *\/ */
    /*     /\*         params.b * params.h, dprops->multiProcessorCount, *\/ */
    /*     /\*         ctas_per_sm, params.seqlen_k, blocksize_c, params.is_causal *\/ */
    /*     /\*     ); *\/ */
    /*     /\* } *\/ */
    /*     if (configure) return; */
    /*     /\* if (params.num_splits == 1) { *\/ */
    /*         dim3 grid_n(params.b, params.h, params.num_splits); */
    /*         kernel<<<grid_n, Kernel_traits::THREADS, smem_size_dq_dk_dv, stream>>>(params); */
    /*     /\* } else { *\/ */
    /*     /\*     dim3 grid_m(params.b, params.h, (params.seqlen_q + 128 - 1) / 128); *\/ */
    /*     /\*     flash_bwd_dot_do_o_kernel<Kernel_traits><<<grid_m, Kernel_traits::THREADS, 0, stream>>>(params); *\/ */
    /*     /\*     int num_splits = params.seqlen_k / blocksize_c;  // seqlen_k is divisible by blocksize_c *\/ */
    /*     /\*     dim3 grid_n(params.b, params.h, num_splits); *\/ */
    /*     /\*     kernel_seqparallel<<<grid_n, Kernel_traits::THREADS, smem_size_dq_dk_dv, stream>>>(params); *\/ */
    /*     /\* } *\/ */
    /*     C10_CUDA_KERNEL_LAUNCH_CHECK(); */
    /* }); */
    if (configure) return;
    // dim3 grid(params.b, params.h);
    const int num_m_block = (params.seqlen_q + Kernel_traits::kBlockM - 1) / Kernel_traits::kBlockM;
    dim3 grid_m(num_m_block, params.b, params.h);
    const int num_n_block = (params.seqlen_k + Kernel_traits::kBlockN - 1) / Kernel_traits::kBlockN;
    dim3 grid_n(num_n_block, params.b, params.h);

    flash_bwd_dot_do_o_kernel<true, Kernel_traits><<<grid_m, Kernel_traits::kNThreads, 0, stream>>>(params);
    // flash_bwd_clear_dkvaccum_kernel<Kernel_traits><<<grid_n, Kernel_traits::kNThreads, 0, stream>>>(params);
    C10_CUDA_KERNEL_LAUNCH_CHECK();

    // We also use is_even_M to set Unpadded in the BlockInfo constructor, so we need to check
    // for cu_seqlens_q as well.
    const bool is_even_M = params.cu_seqlens_q == nullptr && params.cu_seqlens_k == nullptr && params.seqlen_q % Kernel_traits::kBlockM == 0;
    const bool is_even_N = params.cu_seqlens_q == nullptr && params.cu_seqlens_k == nullptr && params.seqlen_k % Kernel_traits::kBlockN == 0;
    const bool is_even_K = params.d == Kernel_traits::kHeadDim;
    constexpr int smem_size_dq_dk_dv = Kernel_traits::kSmemSize;
    // constexpr int smem_size_dq_dk_dv = Kernel_traits::kSmemSize1rowblock;
    BOOL_SWITCH(params.p_dropout < 1.f, IsDropoutConst, [&] {
        BOOL_SWITCH(params.is_causal, IsCausalConst, [&] {
            BOOL_SWITCH(is_even_M, IsEvenMConst, [&] {
            // BOOL_SWITCH(is_even_N, IsEvenNConst, [&] {
                BOOL_SWITCH(is_even_K, IsEvenKConst, [&] {
                    // auto kernel = &flash_bwd_dq_dk_dv_loop_kernel<Kernel_traits, IsDropoutConst, IsCausalConst>;
                    auto kernel = &flash_bwd_dq_dk_dv_loop_seqq_parallel_kernel<Kernel_traits, IsDropoutConst, IsCausalConst, IsEvenMConst, IsEvenKConst>;
                    // auto kernel = &flash_bwd_dq_dk_dv_loop_seqk_parallel_kernel<Kernel_traits, IsDropoutConst, IsCausalConst, IsEvenNConst, IsEvenKConst>;
                    if (smem_size_dq_dk_dv >= 48 * 1024)  {
                        C10_CUDA_CHECK(cudaFuncSetAttribute(
                            kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, smem_size_dq_dk_dv));
                    }
                    // kernel<<<grid_n, Kernel_traits::kNThreads, smem_size_dq_dk_dv, stream>>>(params);
                    kernel<<<grid_m, Kernel_traits::kNThreads, smem_size_dq_dk_dv, stream>>>(params);
                    C10_CUDA_KERNEL_LAUNCH_CHECK();
                });
            });
        });
    });

    auto kernel_dq = &flash_bwd_convert_dq_kernel<Kernel_traits>;
    if (Kernel_traits::kSmemdQSize >= 48 * 1024)  {
        C10_CUDA_CHECK(cudaFuncSetAttribute(
            kernel_dq, cudaFuncAttributeMaxDynamicSharedMemorySize, Kernel_traits::kSmemdQSize));
    }
    kernel_dq<<<grid_m, Kernel_traits::kNThreads, Kernel_traits::kSmemdQSize, stream>>>(params);
    // auto kernel_dkv = &flash_bwd_convert_dkv_kernel<Kernel_traits>;
    // if (Kernel_traits::kSmemKVSize >= 48 * 1024)  {
    //     C10_CUDA_CHECK(cudaFuncSetAttribute(
    //         kernel_dkv, cudaFuncAttributeMaxDynamicSharedMemorySize, Kernel_traits::kSmemKVSize));
    // }
    // kernel_dkv<<<grid_n, Kernel_traits::kNThreads, Kernel_traits::kSmemKVSize, stream>>>(params);
    C10_CUDA_KERNEL_LAUNCH_CHECK();
}
//
