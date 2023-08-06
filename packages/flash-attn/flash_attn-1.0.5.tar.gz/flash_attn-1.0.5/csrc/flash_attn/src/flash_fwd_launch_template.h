/******************************************************************************
 * Copyright (c) 2023, Tri Dao.
 ******************************************************************************/

#pragma once

#include "static_switch.h"
#include "flash.h"
#include "flash_fwd_kernel.h"

template<typename Kernel_traits, bool Is_dropout, bool Is_causal, bool Is_even_N, bool Is_even_K, bool Return_softmax>
__global__ void flash_fwd_loop_kernel(Flash_fwd_params params) {
    flash::compute_attn<Kernel_traits, Is_dropout, Is_causal, Is_even_N, Is_even_K, Return_softmax>(params);
}

template<typename Kernel_traits, bool Is_dropout>
void run_flash_loop_(Flash_fwd_params &params, cudaStream_t stream) {
    constexpr size_t smem_size = Kernel_traits::kSmemSize;
    // printf("smem_size = %d\n", smem_size);

    // Work-around for gcc 7. It doesn't like nested BOOL_SWITCH.
    // https://github.com/kokkos/kokkos-kernels/issues/349
    // https://github.com/HazyResearch/flash-attention/issues/21

    const int num_m_block = (params.seqlen_q + Kernel_traits::kBlockM - 1) / Kernel_traits::kBlockM;
    dim3 grid(num_m_block, params.b, params.h);
    // We also use is_even_N to set Unpadded in the BlockInfo constructor, so we need to check
    // for cu_seqlens_q as well.
    const bool is_even_N = params.cu_seqlens_q == nullptr && params.cu_seqlens_k == nullptr && params.seqlen_k % Kernel_traits::kBlockN == 0;
    const bool is_even_K = params.d == Kernel_traits::kHeadDim;
    const bool return_softmax = params.p_ptr != nullptr;
    BOOL_SWITCH(params.is_causal, IsCausalConst, [&] {
        BOOL_SWITCH(is_even_N, IsEvenNConst, [&] {
            BOOL_SWITCH(is_even_K, IsEvenKConst, [&] {
                BOOL_SWITCH(return_softmax, ReturnSoftmaxConst, [&] {
                    // Will only return softmax if dropout, to reduce compilation time.
                    auto kernel = &flash_fwd_loop_kernel<Kernel_traits, Is_dropout, IsCausalConst, IsEvenNConst, IsEvenKConst, ReturnSoftmaxConst && Is_dropout>;
                    // auto kernel = &flash_fwd_loop_kernel<Kernel_traits, false, false, true, IsEvenKConst, false>;
                    if (smem_size >= 48 * 1024) {
                        C10_CUDA_CHECK(cudaFuncSetAttribute(
                            kernel, cudaFuncAttributeMaxDynamicSharedMemorySize, smem_size));
                    }
                    kernel<<<grid, Kernel_traits::kNThreads, smem_size, stream>>>(params);
                    C10_CUDA_KERNEL_LAUNCH_CHECK();
                });
            });
        });
    });
}
