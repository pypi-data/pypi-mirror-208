#!/usr/bin/env python3
# #******************************************************************************#
# # Copyright(c) 2019-2023, Elemento srl, All rights reserved                    #
# # Author: Elemento srl                                                         #
# # Contributors are mentioned in the code where appropriate.                    #
# # Permission to use and modify this software and its documentation strictly    #
# # for personal purposes is hereby granted without fee,                         #
# # provided that the above copyright notice appears in all copies               #
# # and that both the copyright notice and this permission notice appear in the  #
# # supporting documentation.                                                    #
# # Modifications to this work are allowed for personal use.                     #
# # Such modifications have to be licensed under a                               #
# # Creative Commons BY-NC-ND 4.0 International License available at             #
# # http://creativecommons.org/licenses/by-nc-nd/4.0/ and have to be made        #
# # available to the Elemento user community                                     #
# # through the original distribution channels.                                  #
# # The authors make no claims about the suitability                             #
# # of this software for any purpose.                                            #
# # It is provided "as is" without express or implied warranty.                  #
# #******************************************************************************#
#
# #------------------------------------------------------------------------------#
# #elemento-monorepo-server                                                      #
# #Authors:                                                                      #
# #- Gabriele Gaetano Fronze' (gfronze at elemento.cloud)                        #
# #- Filippo Valle (fvalle at elemento.cloud)                                    #
# #------------------------------------------------------------------------------#
#


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
