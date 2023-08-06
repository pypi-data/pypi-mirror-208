#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from cpu.cpustatus import corestatus, MAX_OVERPROVISION_DEFAULT


class TestCoreStatus(unittest.TestCase):

    def test_Constructor(self):
        for SMTRatio in range(1, 5):
            stat = corestatus(SMTRatio=SMTRatio)
            self.assertTrue(isinstance(stat.provisionCounters, list))
            self.assertTrue(len(stat.provisionCounters) == SMTRatio)
            self.assertTrue(isinstance(stat.maxOverprovisions, list))
            self.assertTrue(len(stat.maxOverprovisions) == SMTRatio)
            self.assertEqual(stat.isSMT, (SMTRatio > 1))

    def test_GetAvailable(self):
        for SMTRatio in range(1, 5):
            stat = corestatus(SMTRatio=SMTRatio)
            self.assertEqual(stat.getAvailable(fullPhysical=False), SMTRatio)
            self.assertEqual(stat.getAvailable(fullPhysical=True), 1)

    def test_GetStricterOverprovision(self):
        for SMTRatio in range(1, 5):
            stat = corestatus(SMTRatio=SMTRatio)
            self.assertEqual(stat.getStricterOverprovision(), MAX_OVERPROVISION_DEFAULT)

            stat.maxOverprovisions[0].append(1)
            self.assertEqual(stat.getStricterOverprovision(), 1)
            self.assertEqual(stat.getStricterOverprovision(0), 1)
            for i in range(1, SMTRatio):
                self.assertEqual(stat.getStricterOverprovision(i), MAX_OVERPROVISION_DEFAULT)

    def test_SMTCompatible(self):
        stat = corestatus(SMTRatio=2)
        self.assertTrue(stat.SMTCompatible(1))
        self.assertTrue(stat.SMTCompatible(2))
        self.assertFalse(stat.SMTCompatible(3))
        self.assertFalse(stat.SMTCompatible(3, allowLeftovers=True))
        stat = corestatus(SMTRatio=4)
        self.assertTrue(stat.SMTCompatible(1))
        self.assertTrue(stat.SMTCompatible(2))
        self.assertTrue(stat.SMTCompatible(4))
        self.assertFalse(stat.SMTCompatible(3))
        self.assertTrue(stat.SMTCompatible(3, allowLeftovers=True))
        self.assertFalse(stat.SMTCompatible(5))
        self.assertFalse(stat.SMTCompatible(5, allowLeftovers=True))

    def test_CanAllocate(self):
        stat = corestatus(SMTRatio=2)
        self.assertTrue(stat.canAllocate())
        self.assertTrue(stat.canAllocate(2, fullPhysical=False))
        self.assertFalse(stat.canAllocate(3, fullPhysical=False))

        stat = corestatus(SMTRatio=4)
        self.assertTrue(stat.canAllocate())
        self.assertTrue(stat.canAllocate(2, fullPhysical=False))
        self.assertTrue(stat.canAllocate(3, fullPhysical=False))
        self.assertTrue(stat.canAllocate(4, fullPhysical=False))
        self.assertFalse(stat.canAllocate(5, fullPhysical=False))

    def test_RegisterSpec(self):
        stat = corestatus(SMTRatio=2)
        stat.registerSpec(uniqueID=0, maxOverprovision=1)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 0)

        stat = corestatus(SMTRatio=2)
        stat.registerSpec(uniqueID=0, maxOverprovision=2)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 2)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)
        self.assertEqual(stat.getAvailable(fullPhysical=False, maxOverprovision=2), 2)
        self.assertEqual(stat.getAvailable(fullPhysical=True, maxOverprovision=2), 1)
        self.assertEqual(stat.getAvailable(fullPhysical=False, maxOverprovision=1), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True, maxOverprovision=1), 0)

        stat = corestatus(SMTRatio=2)
        stat.registerSpec(uniqueID=0, slots=1, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 2)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)
        self.assertEqual(stat.getAvailable(fullPhysical=False, maxOverprovision=1), 1)
        self.assertEqual(stat.getAvailable(fullPhysical=True, maxOverprovision=1), 0)

        stat = corestatus(SMTRatio=2)
        stat.registerSpec(uniqueID=0, slots=1, fullPhysical=False, maxOverprovision=2)
        stat.registerSpec(uniqueID=1, slots=1, fullPhysical=False, maxOverprovision=2)
        stat.registerSpec(uniqueID=2, slots=1, fullPhysical=False, maxOverprovision=2)
        stat.registerSpec(uniqueID=3, slots=1, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=False, maxOverprovision=1), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True, maxOverprovision=1), 0)

        stat = corestatus(SMTRatio=2)
        stat.registerSpec(uniqueID=0, slots=1, fullPhysical=False, maxOverprovision=2)
        stat.registerSpec(uniqueID=1, slots=1, fullPhysical=False, maxOverprovision=6)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 1)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 0)
        stat.registerSpec(uniqueID=2, slots=1, fullPhysical=False, maxOverprovision=5)
        stat.registerSpec(uniqueID=3, slots=1, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=False, maxOverprovision=1), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True, maxOverprovision=1), 0)

    def test_UnregisterSpec(self):
        stat = corestatus(SMTRatio=2)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 2)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)
        stat.registerSpec(uniqueID=0, maxOverprovision=1)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 0)
        stat.unregisterSpec(uniqueID=0)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 2)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)

        stat = corestatus(SMTRatio=4)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 4)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)
        stat.registerSpec(uniqueID=0, maxOverprovision=1)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 0)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 0)
        stat.unregisterSpec(uniqueID=0)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 4)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)

        stat = corestatus(SMTRatio=2)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 2)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)
        stat.registerSpec(uniqueID=0, slots=1, fullPhysical=False, maxOverprovision=1)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 1)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 0)
        stat.unregisterSpec(uniqueID=0)
        self.assertEqual(stat.getAvailable(fullPhysical=False), 2)
        self.assertEqual(stat.getAvailable(fullPhysical=True), 1)


if __name__ == '__main__':
    unittest.main()
