#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from pcidev.pcistatus import pciaddress


class TestPCIAddress(unittest.TestCase):
    def test_Constructor_Short(self):
        addr = pciaddress("56:78.9")
        self.assertEqual(addr.domain, "0000")
        self.assertEqual(addr.bus, "56")
        self.assertEqual(addr.slot, "78")
        self.assertEqual(addr.function, "9")

    def test_Constructor_Full(self):
        addr = pciaddress("1234:56:78.9")
        self.assertEqual(addr.domain, "1234")
        self.assertEqual(addr.bus, "56")
        self.assertEqual(addr.slot, "78")
        self.assertEqual(addr.function, "9")

    def test_GetReadable(self):
        string = "1234:56:78.9"
        addr = pciaddress(string)
        self.assertEqual(addr.getReadable(), string)


if __name__ == '__main__':
    unittest.main()
