#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from pcidev.pcirequirements import pcirequirements
from pcidev.pcistatus import pcistatus


class TestPCIStatus(unittest.TestCase):
    def test_GetAvailable(self):
        stat = pcistatus(test_mode=True)
        self.assertEqual(stat.getAvailable("10de:1bb1"), 2)
        self.assertEqual(stat.getAvailable("8086:3e1f"), 1)

    def test_CanAllocate(self):
        stat = pcistatus(test_mode=True)
        self.assertTrue(stat.canAllocate(pcirequirements(["8086:3e1f"])))
        self.assertTrue(stat.canAllocate(pcirequirements(["10de:1bb1"])))
        self.assertTrue(stat.canAllocate(pcirequirements(["10de:1bb1", "10de:1bb1"])))
        self.assertTrue(stat.canAllocate(pcirequirements(["10de:1bb1", "8086:3e1f"])))
        self.assertFalse(stat.canAllocate(pcirequirements(["dead:beef"])))
        self.assertFalse(stat.canAllocate(pcirequirements(["10de:1bb1", "10de:1bb1", "10de:1bb1"])))

    def test_RegisterSpec(self):
        stat = pcistatus(test_mode=True)
        self.assertEqual(stat.getAvailable("10de:1bb1"), 2)
        self.assertEqual(stat.getAvailable("8086:3e1f"), 1)

        req = pcirequirements(["10de:1bb1", "10de:1bb1"])
        stat.registerSpec(req, 0)

        self.assertEqual(stat.getAvailable("10de:1bb1"), 0)
        self.assertEqual(stat.getAvailable("8086:3e1f"), 1)

        req = pcirequirements(["8086:3e1f"])
        stat.registerSpec(req, 1)

        self.assertEqual(stat.getAvailable("10de:1bb1"), 0)
        self.assertEqual(stat.getAvailable("8086:3e1f"), 0)

    def test_UnregisterSpec(self):
        stat = pcistatus(test_mode=True)
        self.assertEqual(stat.getAvailable("10de:1bb1"), 2)
        self.assertEqual(stat.getAvailable("8086:3e1f"), 1)

        req = pcirequirements(["10de:1bb1", "10de:1bb1"])
        stat.registerSpec(req, 0)
        stat.unregisterSpec(0)

        self.assertEqual(stat.getAvailable("10de:1bb1"), 2)
        self.assertEqual(stat.getAvailable("8086:3e1f"), 1)

        req = pcirequirements(["8086:3e1f"])
        stat.registerSpec(req, 0)
        stat.unregisterSpec(0)

        self.assertEqual(stat.getAvailable("10de:1bb1"), 2)
        self.assertEqual(stat.getAvailable("8086:3e1f"), 1)


if __name__ == '__main__':
    unittest.main()
