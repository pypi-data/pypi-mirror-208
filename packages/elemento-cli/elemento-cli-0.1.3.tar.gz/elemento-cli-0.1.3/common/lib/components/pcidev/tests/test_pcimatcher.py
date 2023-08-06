#!/usr/bin/env python3

import sys
import os
module_name = os.path.abspath(__file__).rsplit("tests", 1)[0].rsplit("/", 2)[1]
base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(module_name, 1)[0]
sys.path.append(base_path)

import unittest
from pcidev.pcirequirements import pcirequirements
from pcidev.pcistatus import pcistatus
from pcidev.pcimatcher import pcimatcher


class TestPCIMatcher(unittest.TestCase):

    def test_PCIMatcher(self):
        stat = pcistatus(test_mode=True)
        req_possible = pcirequirements(["10de:1bb1", "10de:1bb1"])
        req_impossible = pcirequirements(["dead:beef"])

        self.assertTrue(pcimatcher(req_possible, stat))
        self.assertFalse(pcimatcher(req_impossible, stat))


if __name__ == '__main__':
    unittest.main()
