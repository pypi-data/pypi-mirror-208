#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from cpu.cpustatus import cpustatus, coresstatus
from cpu.cpurequirements import cpurequirements
from cpu.cpumatcher import cpumatcher

N_PHYSICAL = 4
IS_SMT = True
SMT_RATIO = 2
N_SMT = N_PHYSICAL * (SMT_RATIO - 1) * int(IS_SMT)
TOTAL_CORES = N_PHYSICAL + N_SMT


def getTestCoresStatus():
    return coresstatus(nPhysical=N_PHYSICAL, SMTRatio=SMT_RATIO)


def getTestCPUStatus():
    stat = cpustatus()
    stat.cpudesc.physicalCores = N_PHYSICAL
    stat.cpudesc.SMTratio = SMT_RATIO
    stat.cpudesc.smtOn = True
    stat.cpudesc.arch = "X86_64"
    stat.cpudesc.extensionFlags = ['SSE', 'SSE2']
    stat.cores = getTestCoresStatus()
    return stat


class TestCPUDescriptor(unittest.TestCase):

    def test_Matching(self):
        stat = getTestCPUStatus()
        print(stat)

        print("Matching single-core, ARM7 -> expected False")
        self.assertFalse(cpumatcher(cpurequirements(1, True, arch=['ARM_7']), stat))

        print("Matching single-core, X86_64 -> expected True")
        self.assertTrue(cpumatcher(cpurequirements(1, True, arch=['X86_64']), stat))

        print("Matching single-thread, X86_64 -> expected True")
        self.assertTrue(cpumatcher(cpurequirements(1, False, arch=['X86_64']), stat))

        print("Matching 2-core, X86_64 -> expected True")
        self.assertTrue(cpumatcher(cpurequirements(2, True, arch=['X86_64']), stat))

        print("Matching 20-core, X86_64 -> expected False")
        self.assertFalse(cpumatcher(cpurequirements(20, True, arch=['X86_64']), stat))

        print("Matching 2-thread, X86_64 and SSE2 -> expected True")
        self.assertTrue(cpumatcher(cpurequirements(2, False, arch=['X86_64']), stat))

        print("Matching 4-core, X86_64 or ARM7 with SSE2 -> expected True")
        self.assertTrue(cpumatcher(cpurequirements(4, True, flags=['sse2'], arch=['X86_64', "ARM_7"]), stat))

        print("Matching 8-core, X86_64 with SSE2 -> expected False")
        self.assertFalse(cpumatcher(cpurequirements(8, True, flags=['sse2'], arch=['X86_64']), stat))

        print("Matching 8-thread, X86_64 with SSE2 -> expected True")
        self.assertTrue(cpumatcher(cpurequirements(8, False, flags=['sse2'], arch=['X86_64']), stat))

        print("Matching 8-thread, X86_64 with AVX-512 -> expected False")
        self.assertFalse(cpumatcher(cpurequirements(8, False, flags=['avx-512f'], arch=['X86_64']), stat))


if __name__ == '__main__':
    unittest.main()
