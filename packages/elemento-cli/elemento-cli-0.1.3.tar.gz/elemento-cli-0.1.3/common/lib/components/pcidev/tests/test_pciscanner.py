#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from pcidev.pcistatus import pciscanner


class TestPCIScanner(unittest.TestCase):
    def test_PCIScanner(self):
        devices = pciscanner(test_mode=True, test_output="00:77.7 0600: 8086:3e1f (rev 08)\n07:00.0 0108: 8086:2522")
        self.assertEqual(devices[0].pciaddr.getReadable(), "0000:00:77.7")
        self.assertEqual(devices[0].pciid, "8086:3e1f")
        self.assertEqual(devices[1].pciaddr.getReadable(), "0000:07:00.0")
        self.assertEqual(devices[1].pciid, "8086:2522")


if __name__ == '__main__':
    unittest.main()
