if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning memstatus unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_memstatus.py")

else:
    from memory.memdescriptor import memdescriptor
    from memory.memrequirements import memrequirements

    class memstatus:
        def __init__(self):
            self.desc = memdescriptor()
            self.runningSpecs = {}
            self.used = 0

        def getAvailable(self):
            return self.desc.capacity - self.used

        def canAllocate(self, req: memrequirements):
            memOk = req.capacity <= self.getAvailable()
            if req.requireECC:
                memOk &= self.desc.isECC
            return memOk

        def registerSpec(self, req: memrequirements, uniqueID: str):
            if not self.canAllocate(req):
                raise Exception("Cannot allocate required MEM spec.")
            else:
                if uniqueID in self.runningSpecs:
                    raise Exception("UniqueID not unique.")
                self.runningSpecs[uniqueID] = req
                self.used += req.capacity
                return uniqueID

        def unregisterSpec(self, uniqueID: str):
            if uniqueID not in self.runningSpecs:
                raise Exception("Spec ID {} not found".format(uniqueID))
            else:
                self.used -= self.runningSpecs[uniqueID].capacity
                del self.runningSpecs[uniqueID]

        def __repr__(self):
            message = '\n\nRAM status\n-------------------------------------------------------------------\n'
            message += self.desc.__repr__()
            message += '\nRunning specs: {}\n'.format(len(self.runningSpecs))
            message += 'Total allocated memory: {}'.format(self.used)

            return message

        def __str__(self):
            return self.__repr__()

    if __name__ == '__main__':
        stat = memstatus()

        print("Allocating 8GB without ECC")
        stat.registerSpec(memrequirements(8e9, False), 0)

        print("Allocating 8GB without ECC")
        stat.registerSpec(memrequirements(8e9, True), 1)

        print("Allocating 16GB without ECC")
        try:
            stat.registerSpec(memrequirements(16e9, False), 1)
        except Exception:
            print("No RAM left!")
