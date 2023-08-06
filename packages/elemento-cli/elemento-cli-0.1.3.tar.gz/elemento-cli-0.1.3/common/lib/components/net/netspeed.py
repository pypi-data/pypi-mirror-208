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
