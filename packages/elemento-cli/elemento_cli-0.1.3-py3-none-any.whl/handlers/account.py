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

import requests
import os
import sys
from tabulate import tabulate
import datetime

os.chdir(os.path.dirname(__file__) + "/../")
sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/common/lib")
sys.path.append(os.getcwd() + "/common/lib/components")
from headers import betterprint, license_headers

import ecd.restkeys as rk
import ecd.networking as networking

from handlers.login import elementoAuthHandler

def createLicenseLine(license):
    if license["is_armed"]:
        expire_date = (datetime.datetime.fromtimestamp(license["expire"]) - datetime.datetime.utcnow()).days
        expire_date = license["expire_date"] + f" ({expire_date} days left)"
    else:
        expire_date = license["expire_date"]
    return [
        license["license_key"],
        license["duration"],
        license["is_armed"],
        expire_date]


def handlerAccount(eah:elementoAuthHandler, parser=None):
    operation = parser.parse_known_args()[0].operation[0]
    if operation == "list_licenses":
        #parser.add_argument('--username', type=bool, required=False)
        #arguments = parser.parse_args()
        with requests.get(
            "http://localhost:"
            + str(networking.AUTH_CLIENT_REST_API_PORT) + rk.AUTH_CLIENT_API_URL_KEY + "/license/list",
            headers={"Content-Type": "application/json"}
        ) as req:
            if req.status_code == 200:
                data = [createLicenseLine(lic) for lic in req.json()["licenses"]]
                betterprint(tabulate(
                    data, headers=license_headers, tablefmt="fancy_grid"))
            else:
                if req.status_code == 205:
                    betterprint(req.json()["detail"])
                else:
                    betterprint(req.text)
                betterprint("You need to login again")
                return 0 if eah.logout() else - 1
    elif operation == "activate_license":
        parser.add_argument('--key', type=str, required=True)
        parser.add_argument('--country', type=str, required=False)
        parser.add_argument('--state', type=str, required=False)
        parser.add_argument('--organization', type=str, required=False)
        parser.add_argument('--unit', type=str, required=False)
        arguments = parser.parse_args()
        with requests.post(
            "http://localhost:"
            + str(networking.AUTH_CLIENT_REST_API_PORT) + rk.AUTH_CLIENT_API_URL_KEY + "/license/arm",
            headers={"Content-Type": "application/json"},
            json={"license_key": arguments.key,
                  "customer": {
                      "Country": arguments.country,
                      "State": arguments.state,
                      "Organization": arguments.organization,
                      "Unit": arguments.unit
                  }
                  }
        ) as req:
            if req.status_code == 200:
                req_json = req.json()
                key = req_json["license"]["key"]
                betterprint(f'License {key} activated')
                betterprint("A file atomos.license has been created")
                with open("atomos.license", "w") as file:
                    file.write(req_json["license"]["file"])
                try:
                    os.system("mkdir -p /etc/elemento/")
                    with open("/etc/elemento/atomos.license", "w") as file:
                        file.write(req_json["license"]["file"])
                except:
                    betterprint("copy atomos.license in /etc/elemento/atomos.license")
            else:
                if req.status_code == 205:
                    betterprint(req.json()["detail"])
                else:
                    betterprint(req.text)
                betterprint("You need to login again")
                return 0 if eah.logout() else - 1
    elif operation == "del_license":
        parser.add_argument('--key', type=str, required=True)
        arguments = parser.parse_args()
        with requests.delete(
            "http://localhost:"
            + str(networking.AUTH_CLIENT_REST_API_PORT) + rk.AUTH_CLIENT_API_URL_KEY + "/license/delete",
            headers={"Content-Type": "application/json"},
            json={"license_key": arguments.key,
                  }
        ) as req:
            if req.status_code == 200:
                req_json = req.json()
                print(req_json)
            else:
                if req.status_code == 205:
                    betterprint(req.json()["detail"])
                else:
                    betterprint(req.text)
                betterprint("You need to login again")
                return 0 if eah.logout() else - 1
    return os.EX_UNAVAILABLE
