#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from cpu.cpudescriptor import cpudescriptor

N_PHYSICAL = 4
IS_SMT = True
SMT_RATIO = 2
N_SMT = N_PHYSICAL * (SMT_RATIO - 1) * int(IS_SMT)
TOTAL_CORES = N_PHYSICAL + N_SMT


class TestCPUDescriptor(unittest.TestCase):

    def test_LogicalCores(self):
        desc = cpudescriptor({'count': N_PHYSICAL, 'smt_ratio': SMT_RATIO})
        self.assertEqual(desc.logicalCores(), N_PHYSICAL * SMT_RATIO)

    def test_GetAvailableCores(self):
        desc = cpudescriptor({'count': N_PHYSICAL, 'smt_ratio': SMT_RATIO})
        self.assertEqual(desc.getAvailableCores(True), N_PHYSICAL * SMT_RATIO)
        self.assertEqual(desc.getAvailableCores(False), N_PHYSICAL)


if __name__ == '__main__':
    unittest.main()
