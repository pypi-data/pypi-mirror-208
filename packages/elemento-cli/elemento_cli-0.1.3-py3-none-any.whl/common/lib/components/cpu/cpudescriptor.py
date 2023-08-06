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

if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning cpudescriptor unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_cpudescriptor.py")

else:
    from cpu.cpuinfo import _get_cpu_info_internal as getcpuinfo

    class cpudescriptor:
        def __init__(self, info=getcpuinfo()):
            self.vendorID = info.get('vendor_id_raw', '')
            self.arch = info.get('arch', '')
            self.physicalCores = info.get('count', '')
            self.SMTratio = info.get('smt_ratio', '')
            self.smtOn = info.get('smt_on', '')
            self.frequency = info.get('hz_advertised_friendly', '')
            self.extensionFlags = [flag.upper().replace("NOW!", "Now!") for flag in info.get('flags', '')]

        def logicalCores(self):
            return self.physicalCores * self.SMTratio

        def getAvailableCores(self, withSMT=True):
            if withSMT:
                return self.logicalCores()
            else:
                return self.physicalCores

        def __repr__(self):
            message = ''
            message += 'Vendor ID: {}'.format(self.vendorID)
            message += '\nArch: {}'.format(self.arch)
            message += '\nPhysical cores: {}'.format(self.physicalCores)
            message += '\nLogical cores: {}'.format(self.logicalCores())
            message += '\nSMT/HT on: {}'.format(self.smtOn)
            message += '\nFrequency: {}'.format(self.frequency)
            message += '\nExtension flags: - {}\n'.format(self.extensionFlags[0])
            for flag in self.extensionFlags[1:]:
                message += '                 - {}\n'.format(flag)
            return message

        def __str__(self):
            return self.__repr__()
