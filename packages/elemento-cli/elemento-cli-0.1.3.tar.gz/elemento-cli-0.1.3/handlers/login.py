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

from asyncore import read
import pickle
import datetime
import requests
import os, sys
import pwinput

os.chdir(os.path.dirname(__file__) + "/../")
sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/common/lib")
sys.path.append(os.getcwd() + "/common/lib/components")
from headers import fh, betterprint, allowed_operations

import ecd.restkeys as rk
import ecd.networking as networking


class AuthError(Exception):
    def __init__(self, f, *args):
        super().__init__(args)
        self.f = f

    def __str__(self):
        return f'Error during authentication {self.f}'


class elementoAuthHandler():
    def __init__(self):
        self.cookie_name = ".elemento_login_cookie"
        self._local_login()

    def _clear_cookie(self):
        if os.path.exists(self.cookie_name):
            os.remove(self.cookie_name)

    def _store_cookie(self, cookie):
        with open(self.cookie_name, "wb") as file:
            pickle.dump(cookie, file)

    def _read_cookie(self) -> dict:
        if os.path.exists(self.cookie_name):
            with open(self.cookie_name, "rb") as file:
                cookie = pickle.load(file)
            return cookie
        else:
            return {"authenticated": False}

    def _authenticate(self, user) -> dict:
        try:
            req = requests.post(f"http://localhost:" + str(networking.AUTH_CLIENT_REST_API_PORT) + rk.AUTH_CLIENT_API_URL_KEY + rk.AUTH_LOGIN,
                               json=user)
            if req.status_code == 200:
                return req.json()
            else:
                print(req.text)
                raise AuthError(req.text)
        except AuthError:
            return {}

    def _deauthenticate(self):
        req = requests.post(f"http://localhost:" + str(networking.AUTH_CLIENT_REST_API_PORT) + rk.AUTH_CLIENT_API_URL_KEY + rk.AUTH_LOGOUT)
        return req.status_code == 200

    def _local_login(self) -> bool:
        cookie = self._read_cookie()
        if cookie["authenticated"] and (
                cookie["timestamp"] - datetime.datetime.utcnow() < datetime.timedelta(days=7)):
            return True
        else:
            self._clear_cookie()
            return False

    def login(self, user=None):
        if user is not None:
            try:
                auth = self._authenticate(user)
                if auth["authenticated"]:
                    self._store_cookie(cookie={
                        "username": user["username"],
                        "authenticated": True,
                        "timestamp": datetime.datetime.utcnow()
                    }
                    )
                    return True
                return False
            except BaseException:
                return self._local_login()
        else:
            return self._local_login()

    def logout(self)->bool:
        try:
            if self._deauthenticate():
                self._clear_cookie()
                return True
            else:
                raise AuthError("Error during logout")
        except:
            return False

    @property
    def loggedIn(self):
        cookie = self._read_cookie()
        return cookie["authenticated"]

def handlerLogin(eah:elementoAuthHandler, parser=None):
    try:
        operation = parser.parse_known_args()[0].operation[0]
        if operation not in allowed_operations["auth"]:
            raise Exception("Not valid operation")
    except:
        operation = "login"
    if operation == "login":
        parser.add_argument('--username', type=bool, required=False)
        #parser.add_argument('--password', type=bool, required=False)
        arguments = parser.parse_args()
        if not eah.loggedIn:
            betterprint("You are not logged in")
            print("Write username")
            if not arguments.username:
                username = input()
            print("Write password")
            psw = pwinput.pwinput(mask="≡")
            if eah.login({"username":username, "password": psw}):
                betterprint("Login successful")
                return 0
            else:
                betterprint("Something went wrong")
                return -1
        elif eah.loggedIn:
            betterprint("You are now logged in")
            return 0
    if operation == "logout":
        return 0 if eah.logout() else - 1

if __name__ == "__main__":
    eah = elementoAuthHandler()
    print(eah.loggedIn)
    eah.login({"username": "admin@test.test", "password": "admin"})
    print(eah.loggedIn)
    eah.logout()
    print(eah.loggedIn)

    eah = elementoAuthHandler()
    print(eah.loggedIn)
    eah.login({"username": "admin@test.test", "password": "admin"})
    print(eah.loggedIn)
    eah = elementoAuthHandler()
    print(eah.loggedIn)
    eah.logout()
