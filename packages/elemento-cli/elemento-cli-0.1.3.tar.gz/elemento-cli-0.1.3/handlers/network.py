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
import jsonpickle
import requests
import json
from tabulate import tabulate

os.chdir(os.path.dirname(__file__) + "/../")
sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/common/lib")
sys.path.append(os.getcwd() + "/common/lib/components")
from headers import betterprint, network_headers


import ecd.restkeys as rk
from ecd.networking import NETWORK_CLIENT_REST_API_PORT


def createNetworkLine(network_json):
    data = [
        network_json["name"],
        network_json["hostname"],
        network_json["speed"],
        network_json["ports"],
        network_json["overprovision"],
    ]
    return data


def handlerNetwork(parser):
    operation = parser.parse_known_args()[0].operation[0]

    if operation == "info":
        try:
            parser.add_argument('ID', type=str)
            arguments = parser.parse_args()
            response = requests.post("http://localhost:"
                                     + str(NETWORK_CLIENT_REST_API_PORT)
                                     + str(rk.NETWORK_CLIENT_API_URL_KEY)
                                     + str(rk.INFO_NETWORK_API_KEY),
                                     json={"local_index": str(arguments.ID)})
            if response.status_code == 200:
                betterprint(response.text)
                return os.EX_OK
            else:
                betterprint("Daemon answered with code {}.".format(response.status_code))
                return os.EX_UNAVAILABLE
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "create":
        try:
            parser.add_argument('--speed', type=str, required=False)
            parser.add_argument('--ports', type=list, required=False)
            parser.add_argument('--spec-json', type=str, required=False)
            arguments = parser.parse_args()
            if arguments.spec_json:
                if ".json" in arguments.spec_json:
                    with open(arguments.spec_json, "r") as file:
                        network = json.load(file)
            else:
                network = {}
                if arguments.speed:
                    network["speed"] = arguments.speed
                if arguments.ports:
                    network["ports"] = ("".join(arguments.ports)).split(",")
            arguments = parser.parse_args()
            response = requests.post("http://localhost:"
                                     + str(NETWORK_CLIENT_REST_API_PORT)
                                     + str(rk.NETWORK_CLIENT_API_URL_KEY)
                                     + str(rk.CREATE_NETWORK_API_KEY),
                                     json=network)
            if response.status_code == 200:
                betterprint("Network created")
                return os.EX_OK
            else:
                betterprint("Daemon answered with code {}.".format(response.status_code))
                return os.EX_UNAVAILABLE
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "destroy":
        try:
            parser.add_argument('ID', type=str)
            arguments = parser.parse_args()
            response = requests.post("http://localhost:"
                                     + str(NETWORK_CLIENT_REST_API_PORT)
                                     + str(rk.NETWORK_CLIENT_API_URL_KEY)
                                     + str(rk.DELETE_NETWORK_API_KEY),
                                     json={"local_index": arguments.ID})
            if response.status_code == 200:
                betterprint("Network destroyed.")
                return os.EX_OK
            else:
                betterprint("Daemon answered with code {}.".format(response.status_code))
                return os.EX_UNAVAILABLE
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "list":
        try:
            arguments = parser.parse_args()
            response = requests.post("http://localhost:"
                                     + str(NETWORK_CLIENT_REST_API_PORT)
                                     + str(rk.NETWORK_CLIENT_API_URL_KEY)
                                     + str(rk.LIST_NETWORKS_API_KEY),
                                     json={})
            if response.status_code == 200:
                data = []
                for network in jsonpickle.loads(response.text):
                    data.append(createNetworkLine(network))
                betterprint(tabulate(data, headers=network_headers, tablefmt="fancy_grid"))
                return os.EX_OK
            else:
                betterprint("Daemon answered with code {}.".format(response.status_code))
                return os.EX_UNAVAILABLE
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE
