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
from cpu.cpustatus import coresstatus

N_PHYSICAL = 4
IS_SMT = True
SMT_RATIO = 2
N_SMT = N_PHYSICAL * (SMT_RATIO - 1) * int(IS_SMT)
TOTAL_CORES = N_PHYSICAL + N_SMT


def getTestCoresStatus():
    return coresstatus(nPhysical=N_PHYSICAL, SMTRatio=SMT_RATIO)


class TestCoresStatus(unittest.TestCase):

    def test_Constructor(self):
        cores = getTestCoresStatus()
        self.assertEqual(cores.totalPhysical, N_PHYSICAL)
        self.assertEqual(cores.totalSMT, N_SMT)
        self.assertEqual(cores.SMTRatio, SMT_RATIO)

        self.assertEqual(len(cores.corestatuses), N_PHYSICAL)
        self.assertEqual(len(cores.runningSpecs), 0)

    def test_GetAvailable_Empty(self):
        cores = getTestCoresStatus()
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=1), 4)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=1), 8)

    def test_RegisterSpec_Core(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=4, fullPhysical=True, maxOverprovision=2)
        self.assertEqual(len(cores.runningSpecs), 1)
        cores.registerSpec(uniqueID=1, slots=4, fullPhysical=True, maxOverprovision=2)
        self.assertEqual(len(cores.runningSpecs), 2)

    def test_RegisterSpec_Thread(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=4, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(len(cores.runningSpecs), 1)
        cores.registerSpec(uniqueID=1, slots=4, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(len(cores.runningSpecs), 2)

    def test_CanAllocate(self):
        cores = getTestCoresStatus()
        self.assertTrue(cores.canAllocate(slots=4, fullPhysical=False))
        self.assertTrue(cores.canAllocate(slots=4, fullPhysical=True))
        self.assertTrue(cores.canAllocate(slots=8, fullPhysical=False))
        self.assertFalse(cores.canAllocate(slots=8, fullPhysical=True))

    def test_GetAvailable_Allocated_Overprovision(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=4, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=2), 4)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=2), 8)

    def test_GetAvailable_Allocated_Core(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=2, fullPhysical=True, maxOverprovision=1)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=2), 2)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=2), 4)
        cores.registerSpec(uniqueID=1, slots=2, fullPhysical=True, maxOverprovision=2)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=2), 2)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=2), 4)

    def test_GetAvailable_Allocated_Thread(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=4, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=1), 2)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=1), 4)
        cores.registerSpec(uniqueID=1, slots=4, fullPhysical=False, maxOverprovision=2)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=1), 2)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=1), 4)

    def test_GetUsedSlots(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=1, fullPhysical=False, maxOverprovision=1)
        self.assertEqual(cores.getUsedSlots(fullPhysical=False), 10)
        self.assertEqual(cores.getUsedSlots(fullPhysical=True), 10)

        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=1, slots=3, fullPhysical=True, maxOverprovision=5)
        self.assertEqual(cores.getUsedSlots(fullPhysical=True), 18)
        self.assertEqual(cores.getUsedSlots(fullPhysical=False), 36)
        cores.registerSpec(uniqueID=2, slots=3, fullPhysical=False, maxOverprovision=10)
        cores.registerSpec(uniqueID=3, slots=3, fullPhysical=False, maxOverprovision=5)
        self.assertEqual(cores.getUsedSlots(fullPhysical=False), 42)
        self.assertEqual(cores.getUsedSlots(fullPhysical=True), 22)

    def test_UnegisterSpec_Core(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=4, fullPhysical=True, maxOverprovision=1)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=1), 0)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=1), 0)
        cores.unregisterSpec(uniqueID=0)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=1), N_PHYSICAL)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=1), N_PHYSICAL + N_SMT)

    def test_UnegisterSpec_Thread(self):
        cores = getTestCoresStatus()
        cores.registerSpec(uniqueID=0, slots=4, fullPhysical=False, maxOverprovision=1)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=1), 2)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=1), 4)
        cores.unregisterSpec(uniqueID=0)
        self.assertEqual(cores.getAvailable(fullPhysical=True, maxOverprovision=1), N_PHYSICAL)
        self.assertEqual(cores.getAvailable(fullPhysical=False, maxOverprovision=1), N_PHYSICAL + N_SMT)


if __name__ == '__main__':
    unittest.main()
