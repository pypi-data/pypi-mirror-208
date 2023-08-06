if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning pcidevice unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_pcidevice.py")

    print("\n\n======================================================================"
          "\nRunning pciscanner unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_pciscanner.py")

    print("\n\n======================================================================"
          "\nRunning pcistatus unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_pcistatus.py")

else:
    from enum import Enum, auto
    import subprocess
    from pcidev.pcirequirements import pcirequirements

    LSPCI_TEST_STRING = "0000:00:77.7 0600: 8086:3e1f (rev 08)\n0000:07:00.0 0108: 8086:2522\n0000:01:00.0 0300: 10de:1bb1 (rev a1)\n0000:01:00.1 0403: 10de:10f0 (rev a1)\n0000:02:00.0 0300: 10de:1bb1 (rev a1)\n0000:02:00.1 0403: 10de:10f0 (rev a1)"  # noqa: E501

    class multisupport(Enum):
        single = auto()
        sriov = auto()
        multi = auto()

    class pciaddress:
        def __init__(self, addressString: str):
            parts = addressString.replace('.', ':').split(':')
            if len(parts) == 4:
                self.domain = parts[0]
                self.bus = parts[1]
                self.slot = parts[2]
                self.function = parts[3]
            elif len(parts) == 3:
                self.domain = '0000'
                self.bus = parts[0]
                self.slot = parts[1]
                self.function = parts[2]
            else:
                self.domain = '0000'
                self.bus = '00'
                self.slot = '00'
                self.function = '0'

        def getGroupKey(self):
            return "{}:{}:{}".format(self.domain, self.bus, self.slot)

        def getReadable(self):
            return "{}.{}".format(self.getGroupKey(), self.function)

    class pcidevice:
        def __init__(self,
                     pciaddr: str = "",
                     pciid: str = "",
                     type: str = "",
                     support: multisupport = multisupport.single):
            self.pciaddr = pciaddress(pciaddr)
            self.pciid = pciid
            self.multisupport = support
            self.type = type
            self.provisionCounter = 0
            self.maxProvision = 1

        def getAvailable(self):
            return int(self.maxProvision - self.provisionCounter)

        def canAllocate(self):
            return self.getAvailable() > 0

    def pciscanner(test_mode=False,
                   test_output=LSPCI_TEST_STRING,
                   allowed_pciids=None):
        if not test_mode:
            try:
                lspci = "lspci -nD"
                process = subprocess.Popen(lspci.split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
                output = output.decode('utf8')
            except Exception:
                print("Using test mode since lspci not found!")
                output = test_output
        else:
            output = test_output

        devices = []
        for line in output.split("\n"):
            parts = line.split(' ')
            if len(parts) < 3:
                continue
            if allowed_pciids:
                try:
                    if parts[2] in allowed_pciids:
                        if(len(parts) >= 3):
                            devices.append(pcidevice(pciaddr=parts[0], pciid=parts[2], type=parts[1].replace(':', '')))
                except IndexError:
                    print(f"Error reading line {parts}. Skipping.")
            else:
                if(len(parts) >= 3):
                    devices.append(pcidevice(pciaddr=parts[0], pciid=parts[2], type=parts[1].replace(':', '')))

        return devices

    class pcistatus:
        def __init__(self, test_mode=False, allowed_pciids=None):
            self.devices = pciscanner(test_mode=test_mode, allowed_pciids=allowed_pciids)
            self.runningSpecs = {}
            self.assignedAddresses = {}

        def getAvailable(self, pciid: str):
            return sum(dev.getAvailable() for dev in self.devices if dev.pciid == pciid)

        def canAllocate(self, req: pcirequirements) -> bool:
            for dev in req.devices:
                if self.getAvailable(dev) < req.devices[dev]:
                    print("Not enough {}".format(dev))
                    return False
            return True

        def assignAndGetAddresses(self, req: pcirequirements):
            assignedaddresses = []
            for dev in req.devices:
                count = req.devices[dev]
                for i, hostdev in enumerate(self.devices):
                    if dev == hostdev.pciid:
                        if hostdev.canAllocate():
                            assignedaddresses.append(hostdev.pciaddr)
                            self.devices[i].provisionCounter += 1
                            count -= 1
                    if count == 0:
                        break

            return assignedaddresses

        def getAssignedAddresses(self, uniqueID: str):
            return self.assignedAddresses[uniqueID]

        def registerSpec(self, req: pcirequirements, uniqueID: str):
            if not self.canAllocate(req):
                raise Exception("Cannot allocate required PCI spec.")
            else:
                if uniqueID in self.runningSpecs or uniqueID in self.assignedAddresses:
                    raise Exception("UniqueID not unique.")
                self.runningSpecs[uniqueID] = req
                self.assignedAddresses[uniqueID] = self.assignAndGetAddresses(req)
                return uniqueID

        def unregisterSpec(self, uniqueID: str):
            if uniqueID not in self.runningSpecs or uniqueID not in self.assignedAddresses:
                raise Exception("Spec ID {} not found".format(uniqueID))
            else:
                for address in self.assignedAddresses[uniqueID]:
                    for hostdev in self.devices:
                        if address == hostdev.pciaddr:
                            hostdev.provisionCounter -= 1
                            hostdev.provisionCounter = max(0, hostdev.provisionCounter)
                del self.assignedAddresses[uniqueID]
                del self.runningSpecs[uniqueID]

        def __repr__(self):
            message = '\n\nPCI subsistem status\n-------------------------------------------------------------------\n'
            message += 'Running specs: {}\n'.format(len(self.runningSpecs))
            message += 'Devices details:\n'
            for dev in self.devices:
                message += '\t{} {} {} {}/{}\n'.format(dev.pciaddr, dev.type,
                                                       dev.pciid, dev.provisionCounter, dev.maxProvision)

            return message

        def __str__(self):
            return self.__repr__()
