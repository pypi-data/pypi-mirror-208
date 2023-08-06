from enum import Enum
from netspeed import netspeed
from typing import List

class porttype(Enum):
    TCP = 1
    UDP = 2
    BOTH = 3

    def tohuman(self):
        if self == porttype.TCP:
            return "TCP"
        if self == porttype.UDP:
            return "UDP"
        if self == porttype.BOTH:
            return "TCP&UDP"


class port:
    def __init__(self, number: int, type: porttype):
        self.number = number
        self.type = type

    def __repr__(self):
        return f"{self.type.tohuman()} {self.number}"


DEFAULT_NET_OVERPROVISION = 10


class netdevice:
    def __init__(self,
                 network_cidr: str,
                 ports: List[port],
                 speed: netspeed,
                 hostname: str = None,
                 overprovision: int = DEFAULT_NET_OVERPROVISION):
        self.net_cidr = network_cidr
        self.ports = ports
        self.speed = speed
        self.hostname = hostname
        self.maxoverprovision = overprovision


class netrequirements:
    def __init__(self, devices: List[netdevice]):
        self.netdevices = devices

    def __repr__(self):
        message = '\nNetwork requirements:'
        for i, d in enumerate(self.netdevices):
            message += "\n\nDevice #: " + str(i)
            message += "\n\tNetwork CIDR: " + d.net_cidr
            message += "\n\tSpeed: " + d.speed.tohuman()
            message += "\n\tHostname: " + d.hostname
            message += "\n\tPorts: " + d.ports.__repr__()
        return message

    def __str__(self):
        return self.__repr__()


if __name__ == "__main__":
    netdevs = [netdevice("192.168.0.0/24",
                         [port(80, porttype.TCP), port(443, porttype.UDP)],
                         netspeed.G1,
                         "test_device"),
               netdevice("172.16.24.0/8",
                         [port(7777, porttype.TCP)],
                         netspeed.G1,
                         "smb")]
    req = netrequirements(netdevs)
    print(req)
