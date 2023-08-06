#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from pcidev.pcirequirements import pcirequirements


class TestPCIRequirements(unittest.TestCase):

    def test_Constructor(self):
        devices = ["8086:1111", "8086:1111", "8086:1112", "8086:1111", "8086:1112", "8086:1113"] + ["8086:1113"] * 5
        req = pcirequirements(devices)
        for dev in devices:
            self.assertEqual(req.devices[dev], devices.count(dev))


if __name__ == '__main__':
    unittest.main()
