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

import json
from tabulate import tabulate
from headers import betterprint
import wget

iso_headers = ["index", "name", "os_family", "os_flavour"]

class ComplexISOException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
    def __str__(self) -> str:
        return "This ISO is not automatically downloadable" + super().__str__()

def handle_isos():
    selection = None
    with open("iso-templates/iso.json", "r") as file:
        isos = json.load(file)

    betterprint(tabulate([(i, iso["name"], iso["os_family"], iso["os_flavour"])
                for i, iso in enumerate(isos)], headers=iso_headers, tablefmt="fancy_grid"))
    print("Select an iso [by index]")
    selection = int(input())
    try:
        if isos[selection]["iso_url"] is None:
            raise ComplexISOException()
        filename = wget.download(isos[selection]["iso_url"], out="/tmp/" + isos[selection]["os_flavour"] + ".iso")
    except Exception as e:
        print(e)
        print("go to {}".format(isos[selection]["help"]))
        flavour = isos[selection]["os_flavour"]
        print(f"and place the downloaded file in /tmp/{flavour}.iso")
