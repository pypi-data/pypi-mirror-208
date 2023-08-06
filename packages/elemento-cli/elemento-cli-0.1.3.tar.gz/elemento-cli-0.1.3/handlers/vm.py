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

import os
import sys
import requests
import json
from si_prefix import si_format
from tabulate import tabulate

os.chdir(os.path.dirname(__file__) + "/../")
sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/common/lib")
sys.path.append(os.getcwd() + "/common/lib/components")
from headers import fh, betterprint, header2_style, vm_headers, pci_headers
from headers import volumes_headers2, templates_headers
from handlers.volumes import createVolumeLine

import ecd.restkeys as rk
from ecd.networking import MATCHER_CLIENT_REST_API_PORT


def createVMLine(vm_json):
    req_json = vm_json["req_json"]
    data = []
    data.append(vm_json["uniqueID"])
    data.append("{} {} {}{}".format(req_json["slots"], req_json["arch"],
                "thread" if req_json["allowSMT"] else "core", 's' if req_json["slots"] > 1 else ''))
    data.append("{} {}".format(si_format(req_json["ramsize"] * 10**9,
                precision=0) + "B", 'ECC' if req_json["reqECC"] else ''))
    data.append("{}".format(req_json["os_family"]))
    if 'network_config' in req_json.keys():
        if "domviewer" in req_json.keys():
            print
            data.append(tabulate(createNetworkConfigLine(req_json=req_json),
                headers=["MAC", "ipv4", "link", "HW link"],
                tablefmt="simple"))
    data.append("{}".format(req_json["netdevs"]))

    pci_data = []
    if "pcidevs" in req_json:
        if len(req_json["pcidevs"]) > 0:
            for dev in req_json["pcidevs"]:
                pci_data.append(createPCILine(dev))

    data.append(tabulate(pci_data, headers=pci_headers, tablefmt="simple") if pci_data else 'None')

    volumes_data = []
    if "volumes" in req_json:
        if len(req_json["volumes"]) > 0:
            for volume in req_json["volumes"]:
                volumes_data.append(createVolumeLine(volume))
            data.append(tabulate(volumes_data, headers=volumes_headers2, tablefmt="simple"))
        else:
            data.append("None")
    else:
        data.append("None")

    return data


def createTemplateLine(template_json):
    data = []
    data.append(fh(template_json['info']['name'], header2_style))
    data.append(template_json['info']['description'])
    data.append("{} {} {}{}".format(template_json["cpu"]["slots"],
                                    ', '.join(template_json["cpu"]["archs"]),
                                    "thread" if template_json["cpu"]["allowSMT"] else "core",
                                    's' if template_json["cpu"]["slots"] > 1 else ''))
    data.append("{} {}".format(si_format(template_json["ram"]["ramsize"] * 10
                ** 6, precision=0) + "B", 'ECC' if template_json["ram"]["reqECC"] else ''))

    pci_data = []
    if "pci" in template_json:
        if len(template_json["pci"]) > 0:
            for dev in template_json["pci"]:
                pci_data.append(createPCILine(dev))

    data.append(tabulate(pci_data, headers=pci_headers, tablefmt="simple") if pci_data else 'None')

    return data


def createPCILine(pci_json):
    data = [
        pci_json["vendor"],
        pci_json["model"],
        pci_json["quantity"]
    ]
    return data

def createNetworkConfigLine(req_json):
    return [[
        req_json["network_config"]["mac"] if req_json["network_config"]["mac"] is not None else "ff:ff:ff:ff:ff:ff",
        req_json["network_config"]["ipv4"] if req_json["network_config"]["ipv4"] is not None else "0.0.0.0",
        req_json["viewer"] if req_json["viewer"] is not None else "",
        req_json["domviewer"] if "domviewer" in req_json.keys() else ""
    ]]


def handlerVM(parser):
    operation = parser.parse_known_args()[0].operation[0]
    if operation == "cancreate":
        try:
            parser.add_argument('spec', type=str)
            parser.add_argument('os_type', choices=["Linux", "Macos", "Windows"], type=str, help="Select desired mode")
            arguments = parser.parse_args()
            status = None
            if arguments.spec.endswith(".json"):
                if os.path.isfile(arguments.spec):
                    json_spec = json.load(open(os.path.abspath(arguments.spec)))
                    if 'misc' not in json_spec:
                        json_spec['misc'] = {}
                        json_spec['misc']['os_family'] = arguments.os_type
                    status = requests.post("http://localhost:"
                                           + str(MATCHER_CLIENT_REST_API_PORT)
                                           + rk.CLIENT_API_URL_KEY
                                           + rk.CANALLOCATE_API_KEY,
                                           json=json_spec)
                else:
                    betterprint("File {} not found.".format(arguments.spec))
                    return os.EX_NOTFOUND
            else:
                templates = requests.get("http://localhost:" + str(MATCHER_CLIENT_REST_API_PORT)
                                         + rk.CLIENT_API_URL_KEY + rk.TEMPLATES_API_KEY)
                selected = list(filter(lambda t: t['info']['name'].lower() == arguments.spec.lower(), templates.json()))
                selected[0]['misc'] = {}
                selected[0]['misc']['os_family'] = arguments.os_type
                if len(selected) == 1:
                    status = requests.post("http://localhost:"
                                           + str(MATCHER_CLIENT_REST_API_PORT)
                                           + rk.CLIENT_API_URL_KEY
                                           + rk.CANALLOCATE_API_KEY,
                                           json=selected[0])
                else:
                    betterprint("Template \"{}\" not found.".format(arguments.spec))
                    return os.EX_NOTFOUND

            if status.status_code == 200:
                betterprint("Availability confirmed by {} Compute Engine{}.".format(
                    status.json()['nservers'], 's' if status.json()['nservers'] > 1 else ''))
                return os.EX_OK
            else:
                betterprint("Cannot allocate this request. No server replied.")
                return os.EX_UNAVAILABLE
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "create":
        try:
            parser.add_argument('--spec-json', type=str)
            parser.add_argument('--volumes-json', type=str)
            arguments = parser.parse_args()
            if os.path.isfile(arguments.volumes_json):
                if arguments.spec_json.endswith(".json"):
                    if os.path.isfile(arguments.spec_json):
                        req = json.load(open(os.path.abspath(arguments.spec_json)))
                        req['volumes'] = json.load(open(os.path.abspath(arguments.volumes_json)))
                        status = requests.post("http://localhost:"
                                               + str(MATCHER_CLIENT_REST_API_PORT)
                                               + rk.CLIENT_API_URL_KEY
                                               + rk.REGISTER_API_KEY,
                                               json=req)
                        return os.EX_OK
                    else:
                        betterprint("Spec file {} not found.".format(arguments.spec_json))
                        return os.EX_NOTFOUND
                else:
                    templates = requests.get("http://localhost:"
                                             + str(MATCHER_CLIENT_REST_API_PORT)
                                             + rk.CLIENT_API_URL_KEY
                                             + rk.TEMPLATES_API_KEY)
                    selected = list(filter(lambda t: t['info']['name'].lower()
                                    == arguments.spec_json.lower(), templates.json()))
                    if len(selected) == 1:
                        req = selected[0]
                        req['volumes'] = json.load(open(os.path.abspath(arguments.volumes_json)))
                        status = requests.post("http://localhost:"
                                               + str(MATCHER_CLIENT_REST_API_PORT)
                                               + rk.CLIENT_API_URL_KEY
                                               + rk.REGISTER_API_KEY,
                                               json=req)
                        return os.EX_OK
                    else:
                        betterprint("Template \"{}\" not found.".format(arguments.req_json))
                        return os.EX_NOTFOUND
            else:
                betterprint("Volumes file {} not found.".format(arguments.volumes_json))
                return os.EX_NOTFOUND
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "list":
        try:
            running = requests.get("http://localhost:"
                                   + str(MATCHER_CLIENT_REST_API_PORT)
                                   + rk.CLIENT_API_URL_KEY
                                   + rk.STATUS_API_KEY)
            data = []
            if running.status_code == 200:
                for vm in running.json():
                    data.append(createVMLine(vm))
                betterprint(tabulate(data, headers=vm_headers, tablefmt="fancy_grid"))
                return os.EX_OK
            else:
                raise Exception(running.text)
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "destroy":
        try:
            parser.add_argument('ID', type=str)
            arguments = parser.parse_args()
            status = requests.post("http://localhost:"
                                   + str(MATCHER_CLIENT_REST_API_PORT)
                                   + rk.CLIENT_API_URL_KEY
                                   + rk.UNREGISTER_API_KEY,
                                   json={"local_index": arguments.ID})
            return os.EX_OK if status.status_code == 200 else os.EX_TEMPFAIL
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "gettemplates":
        try:
            templates = requests.get("http://localhost:"
                                     + str(MATCHER_CLIENT_REST_API_PORT)
                                     + rk.CLIENT_API_URL_KEY
                                     + rk.TEMPLATES_API_KEY)
            data = []
            for template in templates.json():
                data.append(createTemplateLine(template))
            betterprint(tabulate(data, headers=templates_headers, tablefmt="fancy_grid"))
            return os.EX_OK
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "getiso":
        try:
            from handlers.iso import handle_isos
            handle_isos()
            return os.EX_OK
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    return os.EX_UNAVAILABLE
