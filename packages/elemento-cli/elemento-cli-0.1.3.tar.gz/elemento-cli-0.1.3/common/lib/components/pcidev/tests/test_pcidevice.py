#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from pcidev.pcistatus import pcidevice


class TestPCIDevice(unittest.TestCase):
    def test_CanAllocate(self):
        dev = pcidevice()
        self.assertTrue(dev.canAllocate())
        dev.provisionCounter = 1
        self.assertFalse(dev.canAllocate())

    def test_GetAvailable(self):
        dev = pcidevice()
        self.assertEqual(dev.getAvailable(), 1)
        dev.provisionCounter = 1
        self.assertEqual(dev.getAvailable(), 0)


if __name__ == '__main__':
    unittest.main()
