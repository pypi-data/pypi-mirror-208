#!python
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
import argparse
import requests

os.chdir(os.path.dirname(__file__))
sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/common/lib")
sys.path.append(os.getcwd() + "/common/lib/components")

from ecd.networking import MATCHER_CLIENT_REST_API_PORT, STORAGE_CLIENT_REST_API_PORT, NETWORK_CLIENT_REST_API_PORT, AUTH_CLIENT_REST_API_PORT

from headers import fh, header2_style
from headers import allowed_operations

from handlers.vm import handlerVM
from handlers.volumes import handlerVolume
from handlers.network import handlerNetwork
from handlers.login import elementoAuthHandler, handlerLogin
from handlers.account import handlerAccount


def pingRESTLocalClient(port):
    try:
        status = requests.get("http://localhost:{}/".format(port))
        return status.status_code == 200
    except Exception as e:
        print(e)
        return False


def handlerInfo(args):
    auth_client_status = pingRESTLocalClient(port=AUTH_CLIENT_REST_API_PORT)
    print("Authz client {}.".format(fh("online" if auth_client_status else "offline", header2_style)))
    
    matcher_client_status = pingRESTLocalClient(port=MATCHER_CLIENT_REST_API_PORT)
    print("Matcher client {}.".format(fh("online" if matcher_client_status else "offline", header2_style)))

    storage_client_status = pingRESTLocalClient(port=STORAGE_CLIENT_REST_API_PORT)
    print("Storage client {}.".format(fh("online" if storage_client_status else "offline", header2_style)))

    network_client_status = pingRESTLocalClient(port=NETWORK_CLIENT_REST_API_PORT)
    print("Network client {}.".format(fh("online" if network_client_status else "offline", header2_style)))

    return os.EX_OK if matcher_client_status and storage_client_status else os.EX_NOHOST


def elementoCLI(args, parser):
    eah = elementoAuthHandler()
    if (not eah.loggedIn) or args.mode == "auth":
        return handlerLogin(eah, parser=parser)
    if args.mode == "vm":
        return handlerVM(parser=parser)
    if args.mode == "volume":
        return handlerVolume(parser=parser)
    if args.mode == "network":
        return handlerNetwork(parser=parser)
    if args.mode == "account":
        return handlerAccount(eah, parser=parser)
    if args.mode == "info":
        return handlerInfo(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Elemento Command Line Interface.')
    parser.add_argument(
        'mode',
        choices=[
            "auth",
            "vm",
            "volume",
            #"network",
            "account",
            "info"],
        type=str,
        help="Select desired mode")
    operation_arg = parser.add_argument('operation', nargs='?', type=str, help="Select desired operation")
    error_state = False
    selected_mode = None
    try:
        selected_mode = sys.argv[1]

        if len(allowed_operations[selected_mode]) > 1:
            selected_operation = sys.argv[2]
            operation_arg.choices = allowed_operations[selected_mode]
            operation_arg.nargs = 1
        else:
            operation_arg.choices = allowed_operations[selected_mode]
            operation_arg.default = [allowed_operations[selected_mode][0]]
            operation_arg.nargs = 1

        args = parser.parse_known_args()[0]
    except Exception:
        error_state = True
        parser.print_usage()

        if selected_mode:
            if selected_mode and selected_mode in allowed_operations:
                print("Valid operations for mode {}: {}".format(
                    selected_mode, ', '.join(allowed_operations[selected_mode])))

    if not error_state:
        os._exit(elementoCLI(args=args, parser=parser))
