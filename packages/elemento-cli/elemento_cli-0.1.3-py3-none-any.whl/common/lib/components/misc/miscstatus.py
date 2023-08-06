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
          "\nRunning miscstatus unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_miscstatus.py")

else:
    import subprocess
    from misc.miscrequirements import miscrequirements

    class miscstatus:
        def __init__(self, manufacturer=None):
            if not manufacturer:
                self.manufacturer = None
                try:
                    system_info = subprocess.run("dmidecode -t system".split(), stdout=subprocess.PIPE)
                    for line in system_info.stdout.decode("utf-8").split("\n"):
                        if "Manufacturer: " in line:
                            self.manufacturer = line.replace("Manufacturer: ", '').strip('\t').rstrip('\t').upper()
                except:
                    self.manufacturer = ""
            else:
                self.manufacturer = manufacturer.upper()

            if self.manufacturer:
                self.manufacturer = self.manufacturer.replace(' ', '_')
            else:
                self.manufacturer = ''

        def canAllocate(self, req: miscrequirements):
            return self.manufacturer == req.manufacturer.upper() or req.manufacturer.upper() == "ANY"

        def __repr__(self):
            message = "System manufacturer: {}".format(self.manufacturer.lower().capitalize())
            return message

        def __str__(self):
            return self.__repr__()
