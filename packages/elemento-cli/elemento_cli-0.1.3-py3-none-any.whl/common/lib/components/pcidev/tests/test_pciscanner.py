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
