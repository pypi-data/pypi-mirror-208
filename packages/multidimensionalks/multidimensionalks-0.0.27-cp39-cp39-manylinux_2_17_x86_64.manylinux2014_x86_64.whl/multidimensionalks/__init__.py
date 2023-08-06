from . import pure
from . import avx2
from . import avx512
from cpufeature.extension import CPUFeature


def test(rvs, use_avx=0, **kwargs):
    method = pure
    if use_avx == 1 and not CPUFeature['AVX512vl']:
        print("!!! Warning: AVX512vl instruction set is not supported by your CPU, backing up to pure implementation")
    elif use_avx in (0, 1) and CPUFeature['AVX512vl']:
        method = avx512
    elif use_avx == 2 and not CPUFeature['AVX2']:
        print("!!! Warning: AVX2 instruction set is not supported by your CPU, backing up to pure implementation")
    elif use_avx in (0, 1) and CPUFeature['AVX2']:
        method = avx2

    return method(rvs, **kwargs)
