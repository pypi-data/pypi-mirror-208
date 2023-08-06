if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning corestatus unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_corestatus.py")

    print("\n\n======================================================================"
          "\nRunning coresstatus unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_coresstatus.py")

    print("\n\n======================================================================"
          "\nRunning cpustatus unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_cpustatus.py")

else:
    from cpu.cpudescriptor import cpudescriptor
    from cpu.cpurequirements import cpurequirements

    MAX_OVERPROVISION_DEFAULT = 10

    class cpuallocation:
        def __init__(self, allocatedPhysicalCores, allocatedSMTCores, maxOverprovision):
            self.allocatedPhysicalCores = allocatedPhysicalCores
            self.allocatedSMTCores = allocatedSMTCores
            self.maxOverprovision = maxOverprovision

        def __repr__(self):
            return "Allocated Phys:%s SMT:%s" % (self.allocatedPhysicalCores, self.allocatedSMTCores)

        def __str__(self):
            return self.__repr__()

    class coreallocation:
        def __init__(self, threadIDs, maxOverprovision: int = MAX_OVERPROVISION_DEFAULT):
            self.threadIDs = threadIDs
            self.maxOverprovision = maxOverprovision

    coreID = 0

    class corestatus:
        def __init__(self, SMTRatio: int = 1):
            global coreID
            self.SMTRatio = SMTRatio
            self.provisionCounters = [0 for x in range(SMTRatio)]
            self.maxOverprovisions = [[MAX_OVERPROVISION_DEFAULT] for x in range(SMTRatio)]
            self.isSMT = SMTRatio > 1
            self.ID = coreID
            self.runningSpecs = {}
            self.occupancyOrder = list(range(0, self.SMTRatio))
            coreID += 1

        def getAvailable(self, fullPhysical: bool, maxOverprovision: int = None) -> bool:
            if maxOverprovision:
                count = [self.provisionCounters[i] < min(min(mop), maxOverprovision)
                         for i, mop in enumerate(self.maxOverprovisions)]
            else:
                count = [self.provisionCounters[i] < min(mop) for i, mop in enumerate(self.maxOverprovisions)]

            if not fullPhysical:
                return int(sum(count))
            else:
                return int(all(count))

        def getUsedSlots(self, fullPhysical: bool) -> bool:
            if not fullPhysical:
                count = [MAX_OVERPROVISION_DEFAULT - min(mop) + self.provisionCounters[i]
                         for i, mop in enumerate(self.maxOverprovisions)]
                return int(sum(count))
            else:
                return (MAX_OVERPROVISION_DEFAULT - min([min(mop) for mop in self.maxOverprovisions])) + max(self.provisionCounters)  # noqa: E501

        def getStricterOverprovision(self, threadID: int = None) -> int:
            if threadID:
                return min(self.maxOverprovisions[threadID])
            else:
                return min(map(lambda mop: min(mop), self.maxOverprovisions))

        def SMTCompatible(self, requiredSMTLevel: int, allowLeftovers: bool = False) -> bool:
            if not allowLeftovers:
                return self.SMTRatio % requiredSMTLevel == 0
            else:
                return self.SMTRatio >= requiredSMTLevel

        def canAllocate(self, slots: int = 1, fullPhysical: bool = True, maxOverprovision: int = 0) -> bool:
            if fullPhysical:
                slots = 1

            if slots == 0:
                raise ValueError("Number of threads must be greater than 0.")

            return slots <= self.getAvailable(fullPhysical=fullPhysical, maxOverprovision=maxOverprovision)

        def registerSpec(self,
                         uniqueID: int,
                         slots: int = 1,
                         fullPhysical: bool = True,
                         maxOverprovision: int = None) -> coreallocation:
            if uniqueID in self.runningSpecs:
                raise Exception("Unique ID is not unique!")

            if not self.canAllocate(slots, fullPhysical, maxOverprovision):
                raise Exception("Cannot allocate required core setup. {} {}".format(slots, fullPhysical))

            if maxOverprovision:
                alloc = coreallocation([], maxOverprovision)
            else:
                alloc = coreallocation([])

            if fullPhysical:
                for i in range(0, self.SMTRatio):
                    self.provisionCounters[i] += 1
                    if maxOverprovision:
                        self.maxOverprovisions[i].append(maxOverprovision)
                    alloc.threadIDs.append(i)
            else:
                for i in self.occupancyOrder:
                    if len(alloc.threadIDs) == slots:
                        break

                    if maxOverprovision:
                        valid = self.provisionCounters[i] < min(min(self.maxOverprovisions[i]), maxOverprovision)
                    else:
                        valid = self.provisionCounters[i] < min(self.maxOverprovisions[i])

                    if valid:
                        self.provisionCounters[i] += 1
                        if maxOverprovision:
                            self.maxOverprovisions[i].append(maxOverprovision)
                        alloc.threadIDs.append(i)

                if not len(alloc.threadIDs) == slots:
                    raise Exception("Unable to allocate required Core setup.")

            self.runningSpecs[uniqueID] = alloc

            self.occupancyOrder = [id for id, _ in sorted(
                zip(range(0, self.SMTRatio), self.maxOverprovisions), key=lambda pair: min(pair[1]))]
            return self.runningSpecs.get(uniqueID)

        def unregisterSpec(self, uniqueID: int):
            if uniqueID not in self.runningSpecs:
                raise Exception("Spec ID {} not found".format(uniqueID))

            alloc = self.runningSpecs.get(uniqueID)
            for threadID in alloc.threadIDs:
                self.provisionCounters[threadID] -= 1
                self.maxOverprovisions[threadID].remove(alloc.maxOverprovision)

            del self.runningSpecs[uniqueID]

        def __repr__(self):
            message = ''

            if self.isSMT:
                message += "Core {} - {}-way SMT\n".format(self.ID, self.SMTRatio)
            else:
                message += "Core {} - no SMT\n".format(self.ID)

            for threadID in range(0, self.SMTRatio):
                message += "\tthread {}: {}/{}\n".format(threadID,
                                                         self.provisionCounters[threadID],
                                                         min(self.maxOverprovisions[threadID]))

            return message

        def __str__(self):
            return self.__repr__()

    class coresstatus:
        def __init__(self, nPhysical: int, SMTRatio: int):
            self.totalPhysical = nPhysical
            self.totalSMT = nPhysical * int(SMTRatio - 1)
            self.SMTRatio = int(SMTRatio)
            self.corestatuses = [corestatus(self.SMTRatio) for _ in range(0, self.totalPhysical)]
            self.runningSpecs = {}

        def getMaxAvailable(self, fullPhysical: bool = True):
            return (self.totalPhysical + (0 if fullPhysical else self.totalSMT)) * MAX_OVERPROVISION_DEFAULT

        def getAvailable(self, fullPhysical: bool = True, maxOverprovision: int = MAX_OVERPROVISION_DEFAULT):
            return sum([cs.getAvailable(fullPhysical=fullPhysical,
                                        maxOverprovision=maxOverprovision) for cs in self.corestatuses])

        def getAvailableSlots(self, fullPhysical: bool = True, maxOverprovision: int = None):
            return sum([cs.getAvailableSlots(fullPhysical=fullPhysical) for cs in self.corestatuses])

        def getUsedSlots(self, fullPhysical: bool = True):
            return sum([cs.getUsedSlots(fullPhysical=fullPhysical) for cs in self.corestatuses])

        def canAllocate(self, slots: int, fullPhysical: bool = True, maxOverprovision: int = MAX_OVERPROVISION_DEFAULT):
            return slots <= self.getAvailable(fullPhysical=fullPhysical, maxOverprovision=maxOverprovision)

        def registerSpec(self,
                         uniqueID: int,
                         slots: int,
                         fullPhysical: bool = True,
                         maxOverprovision: int = 0,
                         fixCores: bool = False):
            if uniqueID in self.runningSpecs:
                raise Exception("Unique ID is not unique!")

            if not self.canAllocate(slots, fullPhysical, maxOverprovision):
                if fullPhysical:
                    raise Exception("Not enough available cores. Impossible to allocate.")
                else:
                    raise Exception("Not enough available threads. Impossible to allocate.")

            allocated = 0
            threadIDs = []
            for i, cs in enumerate(self.corestatuses):
                if allocated == slots:
                    break
                available = cs.getAvailable(fullPhysical=fullPhysical, maxOverprovision=maxOverprovision)
                if available == 0:
                    continue
                toAllocate = min(slots - allocated, available)
                alloc = cs.registerSpec(uniqueID=uniqueID, slots=toAllocate,
                                        fullPhysical=fullPhysical, maxOverprovision=maxOverprovision)
                threadIDs += [i * self.SMTRatio + thid for thid in alloc.threadIDs]
                allocated += toAllocate

            self.runningSpecs[uniqueID] = threadIDs

            return uniqueID

        def unregisterSpec(self, uniqueID: int):
            if uniqueID not in self.runningSpecs:
                raise Exception("Spec ID {} not found".format(uniqueID))
                return

            for cs in self.corestatuses:
                if uniqueID in cs.runningSpecs:
                    cs.unregisterSpec(uniqueID)

            del self.runningSpecs[uniqueID]

        def __repr__(self):
            message = ''

            for i, coreit in enumerate(self.corestatuses):
                message += coreit.__repr__()

            return message

        def __str__(self):
            return self.__repr__()

    class cpustatus:
        def __init__(self):
            self.cpudesc = cpudescriptor()
            self.cores = coresstatus(nPhysical=self.cpudesc.physicalCores, SMTRatio=self.cpudesc.SMTratio)
            self.runningSpecs = {}

        def canAllocate(self, req: cpurequirements):
            return self.cores.getAvailable(fullPhysical=req.fullPhysical,
                                           maxOverprovision=req.maxOverprovision) >= req.slots

        def registerSpec(self, req: cpurequirements, uniqueID: str):
            if not self.canAllocate(req):
                raise Exception("Cannot allocate required CPU spec.")

            if uniqueID in self.runningSpecs:
                raise Exception("UniqueID not unique!")

            self.cores.registerSpec(uniqueID=uniqueID, slots=req.slots,
                                    fullPhysical=req.fullPhysical, maxOverprovision=req.maxOverprovision)
            self.runningSpecs[uniqueID] = req

            return uniqueID

        def unregisterSpec(self, uniqueID: str):
            if uniqueID not in self.runningSpecs:
                raise Exception("Spec ID {} not found".format(uniqueID))
            else:
                self.cores.unregisterSpec(uniqueID)
                del self.runningSpecs[uniqueID]

        def __repr__(self):
            message = '\n\nCPU status\n-------------------------------------------------------------------\n'
            message += self.cpudesc.__repr__()
            message += 'Running specs: {}\n'.format(len(self.runningSpecs))
            message += 'Cores details:\n'
            message += self.cores.__repr__()

            return message

        def __str__(self):
            return self.__repr__()
