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

from psutil import virtual_memory
import subprocess


def isECCAvailable():
    try:
        dmidecodeECC = "dmidecode --type 16"
        process = subprocess.Popen(dmidecodeECC.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        return bool("ECC" in output.decode("utf-8"))
    except:
        return False

class memdescriptor:
    def __init__(self):
        self.capacity = virtual_memory().total / 2**20
        self.isECC = isECCAvailable()

    def __repr__(self):
        message = ''
        message += 'Capacity: {}'.format(self.capacity)
        message += '\nIs ECC: {}'.format(self.isECC)
        return message

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    desc = memdescriptor()
    print(desc)
