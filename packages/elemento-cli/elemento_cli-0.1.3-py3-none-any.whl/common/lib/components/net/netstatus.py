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

# if __name__ == '__main__':
#     import os

#     print("\n\n======================================================================"
#           "\nRunning netstatus unittests\n")
#     os.system(os.path.dirname(__file__) + "/tests/test_netstatus.py")

# else:
from cgi import test
from enum import Enum
from itertools import filterfalse, count
from tracemalloc import start
import netifaces
from netspeed import netspeed
from netrequirements import netrequirements, netdevice, port, porttype


class iptype(Enum):
    V4 = 1
    V6 = 2

    def tohuman(self):
        if self == iptype.V4:
            return "IP v4"
        if self == iptype.V6:
            return "IP v6"


class netaddress:
    def __init__(self, data: tuple):
        type = data[0]
        info = data[1][0]
        self.type = iptype.V4
        if type == netifaces.AF_INET:
            self.type = iptype.V4
        if type == netifaces.AF_INET6:
            self.type = iptype.V6

        self.addr = info['addr'].rsplit('%', 1)[0]
        self.mask = info['netmask']
        self.bcast = info['broadcast'] if 'broadcast' in info else None

    def __repr__(self):
        return f"{self.type.tohuman()} address: {self.addr}/{self.mask} {self.bcast}"


def getlinkspeed(name: str, test_mode=False):
    speed = 0
    if test_mode:
        speed = 1000
    else:
        with open(f"/sys/class/net/{name}/speed") as f:
            speed = int(f.read())

    if speed == 10:
        return netspeed.M10
    if speed == 100:
        return netspeed.M100
    if speed == 1000:
        return netspeed.G1
    if speed == 2500:
        return netspeed.G2_5
    if speed == 5000:
        return netspeed.G5
    if speed == 10000:
        return netspeed.G10
    if speed == 25000:
        return netspeed.G25
    if speed == 40000:
        return netspeed.G40
    if speed == 100000:
        return netspeed.G100


class netiface:
    def __init__(self, iface: dict, test_mode=False):
        print(iface)
        self.name = iface[0]
        data = iface[1]
        self.mac = data[netifaces.AF_LINK][0]['addr']
        addr_data = dict((k, v) for k, v in iface[1].items()
                         if ((netifaces.AF_INET == k) or (netifaces.AF_INET6 == k) and ('broadcast' in v)))
        self.addresses = [netaddress(addr) for addr in addr_data.items()]
        self.speed = getlinkspeed(self.name, test_mode=test_mode)
        self.allocatedbandwidths = []

    def canAllocate(self, speed: int):
        return self.speed.toint() >= (speed + sum(s.toint() for s in self.allocatedbandwidths))

    def registerSpec(self, speed: netspeed):
        if not self.canAllocate(speed):
            raise Exception("Cannot allocate required bandwidth.")

        self.allocatedbandwidths.append(speed)

    def unregisterSpec(self, speed: netspeed):
        self.allocatedbandwidths.remove(speed)

    def __repr__(self):
        message = f"Name: {self.name}\n"
        message += f"Speed: {self.speed.tohuman()}\n"
        message += f"MAC: {self.mac}\n"
        message += "Addresses:\n"
        for addr in self.addresses:
            message += f"\t* {addr.__repr__()}\n"
        return message


class netstatus:
    def __init__(self, test_mode=False):
        if test_mode:
            interfaces = [('en0', {18: [{'addr': '88:66:5a:16:69:ff'}],
                                   2: [{'addr': '77.77.77.85',
                                        'netmask': '255.255.255.0',
                                        'broadcast': '77.77.77.255'}]}),
                          ('en1', {18: [{'addr': '88:66:5a:16:69:fe'}],
                                   2: [{'addr': '77.77.77.86',
                                        'netmask': '255.255.255.0',
                                        'broadcast': '77.77.77.255'}]})]
            self.interfaces = [netiface(it, test_mode=test_mode) for it in interfaces]
        else:
            interfaces = dict((i, netifaces.ifaddresses(i)) for i in netifaces.interfaces())
            interfaces = dict((k, v) for k, v in interfaces.items()
                              if ((netifaces.AF_INET in v) or (netifaces.AF_INET6 in v)) and (netifaces.AF_LINK in v))

            self.interfaces = [netiface(it, test_mode=test_mode) for it in interfaces.items()]
        self.interfaces = [ifc for ifc in self.interfaces if len(ifc.addresses) > 0]
        self.runningSpecs = {}
        self.totalband = sum(ifc.speed.toint() for ifc in self.interfaces)

    def computeAllocation(self, req: netrequirements, start_from=0):
        allocation = {}
        if start_from == len(self.interfaces):
            return None
        for d in range(len(req.netdevices), 0, -1):
            total = sum(ifc.speed.toint() for ifc in req.netdevices[0: d])
            remaining = sum(ifc.speed.toint() for ifc in req.netdevices[d:])
            canAllocate = [ifc.canAllocate(total) for ifc in self.interfaces[start_from:]]
            if any(canAllocate):
                for i, c in enumerate(canAllocate):
                    if c:
                        for dev in req.netdevices[0: d]:
                            allocation[dev.hostname] = self.interfaces[i + start_from].name
                        break
                if remaining == 0:
                    return allocation
                else:
                    recurring_allocation = self.computeAllocation(netrequirements(req.netdevices[d:]), start_from + 1)
                    if(recurring_allocation):
                        allocation.update(recurring_allocation)
                    return allocation

            else:
                continue

        return allocation

    def canAllocate(self, req: netrequirements, start_from=0):
        return len(req.netdevices) == len(self.computeAllocation(req))

    def registerSpec(self, req: netrequirements, uniqueID: str):
        if not self.canAllocate(req):
            raise Exception("Cannot allocate required NET spec.")

        if uniqueID in self.runningSpecs:
            raise Exception("UniqueID not unique!")

        allocation = self.computeAllocation(req)

        self.runningSpecs[uniqueID] = allocation

        return uniqueID

    def __repr__(self):
        message = ''
        for i in self.interfaces:
            message += "\n" + i.__repr__()
        message += f"\nTotal bandwidth: {self.totalband} Mbps"
        return message

    def __str__(self):
        return self.__repr__()


if __name__ == "__main__":
    # print('en0', {18: [{'addr': '88:66:5a:16:69:ff'}], 30: [{'addr': 'fe80::1c32:a990:4432:d01', 'netmask': 'ffff:ffff:ffff:ffff::/64', 'flags': 1024}], 2: [{'addr': '172.16.24.85', 'netmask': '255.255.255.0', 'broadcast': '172.16.24.255'}]})
    stat = netstatus(test_mode=True)
    print(stat)
    # stat.interfaces[0]
    # print(stat.interfaces[0].canAllocate(netspeed.G1))
    # stat.interfaces[0].registerSpec(netspeed.G1)
    # print(stat.interfaces[0].canAllocate(netspeed.G1))
    # stat.interfaces[0].unregisterSpec(netspeed.G1)
    # print(stat.interfaces[0].canAllocate(netspeed.G1))

    netdevs = [netdevice("192.168.0.0/24",
                         [port(80, porttype.TCP), port(443, porttype.UDP)],
                         netspeed.G1,
                         "test_device"),
               netdevice("172.16.24.0/8",
                         [port(7777, porttype.TCP)],
                         netspeed.G1,
                         "smb"),
               netdevice("172.16.47.0/8",
                         [port(3389, porttype.TCP)],
                         netspeed.G1,
                         "test")]
    req = netrequirements(netdevs)

    print(stat.canAllocate(req))
