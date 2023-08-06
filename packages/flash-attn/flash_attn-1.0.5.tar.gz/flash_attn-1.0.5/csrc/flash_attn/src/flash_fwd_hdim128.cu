// Copyright (c) 2023, Tri Dao.

// Splitting the different head dimensions to different files to speed up compilation.

#include "flash_fwd_launch_template.h"

template<>
void run_mha_fwd_<128>(Flash_fwd_params &params, cudaStream_t stream) {
    using elem_type = cutlass::half_t;
    if (params.p_dropout == 1.f) {
        // Using 8 warps (128 x 128 and 256 x 64) is 28% slower for seqlen=2k
        run_flash_loop_<Flash_fwd_kernel_traits<128, 128, 64, 4, false, false, elem_type>, false>(params, stream);
    } else {
        run_flash_loop_<Flash_fwd_kernel_traits<128, 128, 32, 4, false, false, elem_type>, true>(params, stream);
    }
}