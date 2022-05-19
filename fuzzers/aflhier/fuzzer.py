import os
import subprocess

from fuzzers.afl import fuzzer as afl_fuzzer
from fuzzers.aflplusplus import fuzzer as aflplusplus_fuzzer


def build():
    """Build benchmark."""
    afl_fuzzer.prepare_build_environment()
    os.environ['CC'] = 'clang'
    os.environ['CXX'] = 'clang++'
    os.environ['FUZZER_LIB'] = '/libQEMU.a'
    aflplusplus_fuzzer.build('qemu')


def fuzz(input_corpus, output_corpus, target_binary):
    """Run fuzzer."""
    # Get LLVMFuzzerTestOneInput address.
    nm_proc = subprocess.run([
        'sh', '-c',
        'nm \'' + target_binary + '\' | grep -i \'T afl_qemu_driver_stdin\''
    ],
                             stdout=subprocess.PIPE,
                             check=True)
    target_func = "0x" + nm_proc.stdout.split()[0].decode("utf-8")
    print('[fuzz] afl_qemu_driver_stdin_input() address =', target_func)

    # Fuzzer options for qemu_mode.
    flags = ['-Q', '-c0']

    os.environ['AFL_QEMU_PERSISTENT_ADDR'] = target_func
    os.environ['AFL_ENTRYPOINT'] = target_func
    os.environ['AFL_QEMU_PERSISTENT_CNT'] = "1000000"
    os.environ['AFL_QEMU_DRIVER_NO_HOOK'] = "1"
    aflplusplus_fuzzer.fuzz(input_corpus,
                            output_corpus,
                            target_binary,
                            flags=flags)
