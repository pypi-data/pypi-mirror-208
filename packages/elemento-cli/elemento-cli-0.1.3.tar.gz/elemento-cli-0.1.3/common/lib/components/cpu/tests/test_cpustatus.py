#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from cpu.cpustatus import coresstatus, cpustatus, cpurequirements

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
    stat.cpudesc.SMTRatio = SMT_RATIO
    stat.cpudesc.smtOn = True
    stat.cores = getTestCoresStatus()
    return stat


class TestCPUStatus(unittest.TestCase):

    def test_CanAllocate(self):
        stat = getTestCPUStatus()
        req1 = cpurequirements(slots=2, fullPhysical=True)
        req2 = cpurequirements(slots=4, fullPhysical=True)
        req3 = cpurequirements(slots=8, fullPhysical=True)
        req4 = cpurequirements(slots=8, fullPhysical=False)

        self.assertTrue(stat.canAllocate(req1))
        self.assertTrue(stat.canAllocate(req2))
        self.assertFalse(stat.canAllocate(req3))
        self.assertTrue(stat.canAllocate(req4))

    def test_RegisterSpec(self):
        stat = getTestCPUStatus()
        self.assertEqual(stat.cores.getAvailable(fullPhysical=False), TOTAL_CORES)
        self.assertEqual(stat.cores.getAvailable(fullPhysical=True), N_PHYSICAL)
        self.assertEqual(stat.registerSpec(cpurequirements(TOTAL_CORES, fullPhysical=False), 12345), 12345)
        self.assertEqual(stat.cores.getAvailable(), 0)

    def test_UnregisterSpec(self):
        stat = getTestCPUStatus()
        self.assertEqual(stat.cores.getAvailable(), N_PHYSICAL)
        stat.registerSpec(cpurequirements(N_PHYSICAL, fullPhysical=True), 12345)
        self.assertEqual(stat.cores.getAvailable(), 0)
        stat.unregisterSpec(12345)
        self.assertEqual(stat.cores.getAvailable(), N_PHYSICAL)


if __name__ == '__main__':
    unittest.main()
