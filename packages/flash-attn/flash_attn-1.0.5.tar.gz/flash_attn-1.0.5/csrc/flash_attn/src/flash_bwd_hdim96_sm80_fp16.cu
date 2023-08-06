// Copyright (c) 2023, Tri Dao.

// Splitting the different head dimensions to different files to speed up compilation.

#include "flash_bwd_launch_template.h"

template<>
void run_mha_bwd_<96>(Flash_bwd_params &params, cudaStream_t stream, const bool configure) {
    using elem_type = cutlass::half_t;
    // run_flash_bwd_loop<Flash_bwd_kernel_traits<96, 64, 128, 8, 2, 4, 4, true, elem_type>>(params, stream, configure);
    // This is very slightly faster
    run_flash_bwd_loop<Flash_bwd_kernel_traits<96, 64, 128, 8, 2, 4, 4, false, elem_type>>(params, stream, configure);
}