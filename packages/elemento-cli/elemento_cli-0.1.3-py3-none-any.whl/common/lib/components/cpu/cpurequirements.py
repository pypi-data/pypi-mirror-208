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

from cpu.common import SUPPORTED_ARCHS, REQ_DEFAULT_ARCH


class cpurequirements:
    def __init__(self, slots: int, fullPhysical: bool, maxOverprovision: int = 1, arch=REQ_DEFAULT_ARCH, flags=[]):
        self.slots = slots
        self.fullPhysical = fullPhysical
        self.maxOverprovision = maxOverprovision

        if isinstance(arch, list):
            for archi in arch:
                if archi not in SUPPORTED_ARCHS:
                    raise ValueError('Supported archs: {}'.format(SUPPORTED_ARCHS))
            self.arch = arch
        else:
            self.arch = [arch]

        if isinstance(flags, list):
            self.flags = flags
        else:
            self.flags = [flags]

    def __repr__(self):
        message = '\nCPU requirements:'
        message += '\n-------------------------------------------------------------------'
        message += '\nRequired arch: {}'.format(' or '.join(self.arch))
        message += '\nRequired slots: {}'.format(self.slots)
        message += '\nAllowed overprovision: {}'.format(self.maxOverprovision)
        message += '\nSlots unit: {}'.format("Cores" if self.fullPhysical else "Threads")
        if self.flags:
            message += '\nRequired extension flags: {}'.format(','.join(self.flags))
        return message

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    req = cpurequirements(4, True, flags=['sse2'])
    print(req)
