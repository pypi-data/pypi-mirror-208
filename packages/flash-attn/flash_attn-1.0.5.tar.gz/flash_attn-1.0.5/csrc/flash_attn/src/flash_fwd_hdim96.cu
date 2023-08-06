// Copyright (c) 2023, Tri Dao.

// Splitting the different head dimensions to different files to speed up compilation.

#include "flash_fwd_launch_template.h"

template<>
void run_mha_fwd_<96>(Flash_fwd_params &params, cudaStream_t stream) {
    using elem_type = cutlass::half_t;
    BOOL_SWITCH(params.p_dropout < 1.f, Is_dropout, [&] {
        run_flash_loop_<Flash_fwd_kernel_traits<96, 128, 64, 4, true, false, elem_type>, Is_dropout>(params, stream);
        // These two are always slower
        // run_flash_loop_<Flash_fwd_kernel_traits<96, 128, 128, 4, true, elem_type>>(params, stream);
        // run_flash_loop_<Flash_fwd_kernel_traits<96, 64, 128, 4, true, elem_type>>(params, stream);
    });
}