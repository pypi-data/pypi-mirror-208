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
from xml.dom import NotFoundErr
import requests
import json
from si_prefix import si_format
from tabulate import tabulate
os.chdir(os.path.dirname(__file__) + "/../")
sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/common/lib")
sys.path.append(os.getcwd() + "/common/lib/components")
from headers import fh, betterprint, volumes_headers, volumes_headers2

import ecd.restkeys as rk
from ecd.networking import STORAGE_CLIENT_REST_API_PORT


def createVolumeLine(volume_json):
    data = [
        volume_json['volumeID'],
        volume_json['name'] if 'name' in volume_json else volume_json['volumeID'],
        si_format(volume_json['size'], precision=0) + "B" if 'nservers' in volume_json else '?',
        volume_json['bootable'],
        volume_json['readonly'],
        volume_json['shareable'],
        volume_json['private'],
        volume_json['own'],
        volume_json['nservers'] if 'nservers' in volume_json else len(volume_json['srvs'])
    ]

    if 'selected_server' in volume_json:
        data.append(volume_json['selected_server'])
    elif 'servers' in volume_json:
        if len(volume_json["servers"]) == 0:
            data.append(volume_json["servers"][0])
        else:
            data.append(', '.join(volume_json["servers"]))
    else:
        data.append('?')
    return data


def handlerVolume(parser):
    operation = parser.parse_known_args()[0].operation[0]

    if operation == "cancreate":
        try:
            parser.add_argument('--size', type=str)
            arguments = parser.parse_args()
            response = requests.post("http://localhost:"
                                     + str(STORAGE_CLIENT_REST_API_PORT)
                                     + rk.STORAGE_CLIENT_API_URL_KEY
                                     + rk.CAN_CREATE_VOLUME_API_KEY,
                                     json={"size": str(arguments.size)})
            if response.status_code == 200:
                if int(response.text) > 0:
                    betterprint("Volume can be created on {} servers".format(response.text))
                else:
                    betterprint("No server available for volume creation.")
                return os.EX_OK
            else:
                betterprint("Daemon answered with code {}.".format(response.status_code))
                return os.EX_UNAVAILABLE
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "create":
        parser.add_argument('--spec-json', type=str, required=False)
        parser.add_argument('--size', type=int, required=False)
        parser.add_argument('--bootable', type=bool, required=False)
        parser.add_argument('--sharable', type=bool, required=False)
        parser.add_argument('--readonly', type=bool, required=False)
        parser.add_argument('--private', type=bool, required=False)
        arguments = parser.parse_args()
        try:
            if arguments.spec_json is not None:
                if arguments.spec_json.endswith(".json"):
                    if os.path.isfile(arguments.spec_json):
                        params = json.load(open(os.path.abspath(arguments.spec_json)))
                    else:
                        betterprint("Spec file {} not found.".format(arguments.spec_json))
                        raise NotFoundErr()
                else:
                    raise Exception("--spec-file must be a json file")
            else:
                arguments = parser.parse_args()
                if arguments.size:
                    params = dict(name="new_volume",
                                  bootable=arguments.bootable if arguments.bootable else False,
                                  readonly=arguments.readonly if arguments.readonly else False,
                                  size=arguments.size,
                                  shareable=arguments.sharable if arguments.sharable else False,
                                  private=arguments.private if arguments.private else False
                                  )
                else:
                    raise Exception("one of --size --spec-json is required")
        except Exception as e:
            print(e)
            return -1
        print(params)
        status = requests.post("http://localhost:"
                               + str(STORAGE_CLIENT_REST_API_PORT)
                               + rk.STORAGE_CLIENT_API_URL_KEY
                               + rk.CREATE_VOLUME_API_KEY,
                               json=params)
        betterprint("Client replied {}".format(status.text))
        if status.status_code == 200:
            return os.EX_OK
        else:
            return -1

    if operation == "info":
        try:
            parser.add_argument('volume_id', type=str)
            arguments = parser.parse_args()
            response = requests.post("http://localhost:"
                                     + str(STORAGE_CLIENT_REST_API_PORT)
                                     + rk.STORAGE_CLIENT_API_URL_KEY
                                     + rk.VOLUME_INFO_API_KEY,
                                     json={"volume_id": arguments.volume_id})
            volume = response.json()
            data = [createVolumeLine(volume)]
            betterprint(tabulate(data, headers=volumes_headers, tablefmt="fancy_grid"))
            return os.EX_OK
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "list":
        try:
            volumes = requests.get("http://localhost:"
                                   + str(STORAGE_CLIENT_REST_API_PORT)
                                   + rk.STORAGE_CLIENT_API_URL_KEY
                                   + rk.ACCESSIBLE_VOLUMES_API_KEY)
            if volumes.status_code == 200:
                try:
                    data = []
                    for volume in list(volumes.json()):
                        data.append(createVolumeLine(volume))
                    betterprint(tabulate(data, headers=volumes_headers, tablefmt="fancy_grid"))
                except BaseException:
                    betterprint(tabulate([], headers=volumes_headers, tablefmt="fancy_grid"))
            elif volumes.status_code == 204:
                betterprint(tabulate([], headers=volumes_headers, tablefmt="fancy_grid"))
            else:
                raise Exception("Server replied " + volumes.status_code)
            return os.EX_OK
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    if operation == "destroy":
        try:
            parser.add_argument('ID', type=str)
            arguments = parser.parse_args()
            status = requests.post("http://localhost:"
                                   + str(STORAGE_CLIENT_REST_API_PORT)
                                   + rk.STORAGE_CLIENT_API_URL_KEY
                                   + rk.DESTROY_VOLUME_API_KEY,
                                   json={"volume_id": arguments.ID})
            return os.EX_OK if status.status_code == 200 else os.EX_TEMPFAIL
        except Exception as e:
            print(e)
            return os.EX_UNAVAILABLE

    return os.EX_UNAVAILABLE
