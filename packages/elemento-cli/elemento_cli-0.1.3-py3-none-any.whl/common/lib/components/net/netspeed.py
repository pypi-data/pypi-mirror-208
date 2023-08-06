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

from enum import Enum


class netspeed(Enum):
    M10 = 1
    M100 = 2
    G1 = 3
    G2_5 = 4
    G5 = 5
    G10 = 6
    G25 = 7
    G40 = 8
    G100 = 9

    def tohuman(self):
        if self == netspeed.M10:
            return "10 Mbit/s"
        if self == netspeed.M100:
            return "100 Mbit/s"
        if self == netspeed.G1:
            return "1 Gbit/s"
        if self == netspeed.G2_5:
            return "2.5 Gbit/s"
        if self == netspeed.G5:
            return "5 Gbit/s"
        if self == netspeed.G10:
            return "10 Gbit/s"
        if self == netspeed.G25:
            return "25 Gbit/s"
        if self == netspeed.G40:
            return "40 Gbit/s"
        if self == netspeed.G100:
            return "100 Gbit/s"

    def fromHuman(speed):
        if speed == "10 Mbit/s":
            return netspeed.M10
        if speed == "100 Mbit/s":
            return netspeed.M100
        if speed == "1 Gbit/s":
            return netspeed.G1
        if speed == "2.5 Gbit/s":
            return netspeed.G2_5
        if speed == "5 Gbit/s":
            return netspeed.G5
        if speed == "10 Gbit/s":
            return netspeed.G10
        if speed == "25 Gbit/s":
            return netspeed.G25
        if speed == "40 Gbit/s":
            return netspeed.G40
        if speed == "100 Gbit/s":
            return netspeed.G100

    def toint(self):
        if self == netspeed.M10:
            return 10
        if self == netspeed.M100:
            return 100
        if self == netspeed.G1:
            return 1000
        if self == netspeed.G2_5:
            return 2500
        if self == netspeed.G5:
            return 5000
        if self == netspeed.G10:
            return 10000
        if self == netspeed.G25:
            return 25000
        if self == netspeed.G40:
            return 40000
        if self == netspeed.G100:
            return 100000
