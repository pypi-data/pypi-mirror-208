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

import jsonpickle

from components.cpu.cpurequirements import cpurequirements
from components.memory.memrequirements import memrequirements
from components.pcidev.pcirequirements import pcirequirements
from components.misc.miscrequirements import miscrequirements


class systemrequirements:
    def __init__(self,
                 cpureq: cpurequirements,
                 memreq: memrequirements,
                 pcireq: pcirequirements = pcirequirements([]),
                 miscreq: miscrequirements = miscrequirements("Any", None)):
        self.cpu = cpureq
        self.mem = memreq
        self.pci = pcireq
        self.misc = miscreq

    def jsonizeToStr(self):
        return jsonpickle.encode(self).replace(' ', '')

    def jsonizeToBytes(self):
        return str.encode(jsonpickle.encode(self).replace(' ', ''))

    def __repr__(self):
        message = 'System requirements\n==================================================================='
        message += self.cpu.__repr__() + "\n"
        message += self.mem.__repr__() + "\n"
        message += self.pci.__repr__() + "\n"
        message += self.misc.__repr__() + "\n"
        message += '\n==================================================================='
        return message

    def __str__(self):
        return self.__repr__()


def getSystemrequirements(reqjson) -> systemrequirements:
    return jsonpickle.decode(reqjson)
