import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.getcwd() + "/components")

from datetime import datetime

from components.cpu.cpustatus import cpustatus
from components.cpu.cpumatcher import cpumatcher
from components.cpu.cpurequirements import cpurequirements
from components.memory.memstatus import memstatus
from components.memory.memmatcher import memmatcher
from components.memory.memrequirements import memrequirements
from components.pcidev.pcistatus import pcistatus
from components.pcidev.pcimatcher import pcimatcher
from components.pcidev.pcirequirements import pcirequirements
from components.misc.miscstatus import miscstatus
from components.misc.miscmatcher import miscmatcher
from system.systemrequirements import systemrequirements


class systemstatus:
    def __init__(self, allowed_pciids=None):
        self.cpu = cpustatus()
        self.mem = memstatus()
        self.pci = pcistatus(allowed_pciids=allowed_pciids)
        self.misc = miscstatus()
        self.runningSpecs = {}

    def canAllocate(self, req: systemrequirements):
        if cpumatcher(req.cpu, self.cpu):
            if memmatcher(req.mem, self.mem):
                if pcimatcher(req.pci, self.pci):
                    if miscmatcher(req.misc, self.misc):
                        return True
                    else:
                        raise Exception("Miscellaneous data prevents allocation.")
                else:
                    raise Exception("Cannot allocate PCI subsystem requests.")
            else:
                raise Exception("Cannot allocate memory requests.")
        else:
            raise Exception("Cannot allocate CPU requests.")

    def registerSpec(self, req: systemrequirements, volumes: dict, uniqueID: str, vm_name: str):
        if not self.canAllocate(req):
            raise Exception("Cannot allocate required SYSTEM spec.")
        else:
            if uniqueID in self.runningSpecs.keys():
                raise Exception("UniqueID not unique.")
            everythingOK = True
            everythingOK &= self.cpu.registerSpec(req.cpu, uniqueID) == uniqueID
            everythingOK &= self.mem.registerSpec(req.mem, uniqueID) == uniqueID
            everythingOK &= self.pci.registerSpec(req.pci, uniqueID) == uniqueID
            if everythingOK:
                pcidevs = []
                for (dev, qty) in req.pci.devices.items():
                    pcidevs.append({'vendor': dev.split(':')[0], 'model': dev.split(':')[1], 'quantity': qty})
                self.runningSpecs[uniqueID] = {
                    'slots': req.cpu.slots,
                    'overprovision': req.cpu.maxOverprovision,
                    'allowSMT': not req.cpu.fullPhysical,
                    'arch': self.cpu.cpudesc.arch,
                    'flags': req.cpu.flags,
                    'ramsize': req.mem.capacity / 1024,
                    'reqECC': req.mem.requireECC,
                    'volumes': volumes,
                    'pcidevs': pcidevs,
                    'netdevs': [],
                    'os_family': req.misc.os_family,
                    'os_flavour': req.misc.os_flavour,
                    'vm_name': vm_name,
                    'creation_date': datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")
                }
                print(self.runningSpecs[uniqueID]['creation_date'])
                return uniqueID
            else:
                self.cpu.unregisterSpec(uniqueID)
                self.mem.unregisterSpec(uniqueID)
                self.pci.unregisterSpec(uniqueID)
                del self.runningSpecs[uniqueID]
                raise Exception("Something went wrong while allocating.")

    def unregisterSpec(self, uniqueID: str):
        if uniqueID not in self.runningSpecs.keys():
            raise Exception("UniqueID not found")
        else:
            self.cpu.unregisterSpec(uniqueID)
            self.mem.unregisterSpec(uniqueID)
            self.pci.unregisterSpec(uniqueID)
            del self.runningSpecs[uniqueID]

    def getRunningSpec(self, uniqueID: str):
        if uniqueID in self.runningSpecs.keys():
            return self.runningSpecs[uniqueID]
        return None

    def getJSONStatus(self):
        resp_json = {}
        resp_json['manufacturer'] = self.misc.manufacturer

        resp_json['cpu'] = {}
        resp_json['cpu']['vendorID'] = self.cpu.cpudesc.vendorID
        resp_json['cpu']['arch'] = self.cpu.cpudesc.arch
        resp_json['cpu']['ncores'] = self.cpu.cpudesc.physicalCores
        resp_json['cpu']['SMTRatio'] = self.cpu.cpudesc.SMTratio
        resp_json['cpu']['SMTOn'] = self.cpu.cpudesc.smtOn
        resp_json['cpu']['frequency'] = self.cpu.cpudesc.frequency
        resp_json['cpu']['flags'] = self.cpu.cpudesc.extensionFlags
        resp_json['cpu']['max_cores'] = self.cpu.cores.getMaxAvailable(fullPhysical=True)
        resp_json['cpu']['used_cores'] = self.cpu.cores.getUsedSlots(fullPhysical=True)
        resp_json['cpu']['max_threads'] = self.cpu.cores.getMaxAvailable(fullPhysical=False)
        resp_json['cpu']['used_threads'] = self.cpu.cores.getUsedSlots(fullPhysical=False)

        resp_json['mem'] = {}
        resp_json['mem']['size'] = self.mem.desc.capacity
        resp_json['mem']['isECC'] = self.mem.desc.isECC
        resp_json['mem']['avail'] = self.mem.getAvailable()

        resp_json['pci'] = []
        for pcidev in self.pci.devices:
            pci_json = {}
            pci_json['pciid'] = pcidev.pciid.split(':')
            pci_json['avail'] = pcidev.getAvailable()
            pci_json['max'] = pcidev.maxProvision
            resp_json['pci'].append(pci_json)
        return resp_json

    def __repr__(self):
        message = 'System status\n==================================================================='
        message += self.cpu.__repr__()
        message += self.mem.__repr__()
        message += self.pci.__repr__()
        message += '\n==================================================================='

        return message

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    stat = systemstatus()

    print('Allocating 4 physical cores with 8GB without ECC and an Nvidia Quadro P4000')
    req = systemrequirements(cpurequirements(4, True, maxOverprovision=2, arch=["X86_64", "ARM_7"], flags="sse2"),
                             memrequirements(8e3, False),
                             pcirequirements(["10de:1bb1"]))
    print(req)
    stat.registerSpec(req, 0)
    print(stat)
