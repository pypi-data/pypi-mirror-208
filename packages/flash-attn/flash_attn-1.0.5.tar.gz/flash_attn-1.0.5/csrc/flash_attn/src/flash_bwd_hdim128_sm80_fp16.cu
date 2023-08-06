// Copyright (c) 2023, Tri Dao.

// Splitting the different head dimensions to different files to speed up compilation.

#include "flash_bwd_launch_template.h"

template<>
void run_mha_bwd_<128>(Flash_bwd_params &params, cudaStream_t stream, const bool configure) {
    using elem_type = cutlass::half_t;
    // run_flash_bwd_loop<Flash_bwd_kernel_traits<128, 32, 128, 8, 2, 2, 2, false, elem_type>>(params, stream, configure);
    // This is faster, in the case of sequence-parallel bwd (where we need fewer registers).
    // Out of these three, the 2nd one is slightly faster (2% faster than the first). Idk why.
    // run_flash_bwd_loop<Flash_bwd_kernel_traits<128, 64, 128, 8, 2, 2, 2, false, elem_type>>(params, stream, configure);
    run_flash_bwd_loop<Flash_bwd_kernel_traits<128, 64, 128, 8, 2, 4, 2, false, elem_type>>(params, stream, configure);
    // run_flash_bwd_loop<Flash_bwd_kernel_traits<128, 64, 128, 8, 2, 4, 4, false, elem_type>>(params, stream, configure);
}