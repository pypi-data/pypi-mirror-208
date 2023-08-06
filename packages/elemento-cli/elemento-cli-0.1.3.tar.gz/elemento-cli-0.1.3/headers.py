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
# #Authors:                                                                      #
# #- Gabriele Gaetano Fronze' (gfronze at elemento.cloud)                        #
# #- Filippo Valle (fvalle at elemento.cloud)                                    #
# #------------------------------------------------------------------------------#
#


from betterprinttable import betterprint

allowed_operations = {
    "auth": ["login", "logout"],
    "vm": ["cancreate", "create", "list", "destroy", "gettemplates", "getiso"],
    "volume": ["cancreate", "create", "list", "info", "destroy"],
    #"network": ["create", "list", "info", "destroy"],
    "account": ["list_licenses", "activate_license", "del_license"],
    "info": ["status"]}

header1_style = "\u001b[1m\u001b[38;5;214m"
header2_style = "\u001b[38;5;221m"


def fh(string, style):
    if string in ["online", "offline"]:
        return style + string + "\u001b[0m\033[0m"
    return string

vm_headers = [fh(header, header1_style)
              for header in ["VM ID", "CPU", "RAM", "OS type", "Network config", "Networks", "PCI devices", "Volumes"]]
templates_headers = [fh(header, header1_style) for header in ["Name", "Description", "CPU", "RAM", "PCI devices"]]
pci_headers = [fh(header, header2_style) for header in ["Vendor", "Model", "Quantity"]]
volumes_headers = [fh(header, header1_style) for header in ["Volume ID", "Name", "Size", "Bootable",
                                                            "Readonly", "Shareable", "Private",
                                                            "Is yours", "# replicas", "Server IP(s)"]]
volumes_headers2 = [fh(header, header2_style) for header in ["Volume ID", "Name", "Size", "Bootable",
                                                             "Readonly", "Shareable", "Private",
                                                             "Is yours", "# replicas", "Server IP(s)"]]
network_headers = [fh(header, header1_style) for header in ["Name", "hostname", "Speed", "Ports", "Overprovisioning"]]
license_headers = [fh(header, header1_style) for header in ["Key", "Duration (days)", "Active", "Expire"]]


# def betterprint(str):
#     print("\n" + str + "\n")

betterprint = betterprint