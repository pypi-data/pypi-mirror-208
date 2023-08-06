from cpu.common import SUPPORTED_ARCHS, REQ_DEFAULT_ARCH


class cpurequirements:
    def __init__(self, slots: int, fullPhysical: bool, maxOverprovision: int = 1, arch=REQ_DEFAULT_ARCH, flags=[]):
        self.slots = slots
        self.fullPhysical = fullPhysical
        self.maxOverprovision = maxOverprovision

        if isinstance(arch, list):
            for archi in arch:
                if archi not in SUPPORTED_ARCHS:
                    raise ValueError('Supported archs: {}'.format(SUPPORTED_ARCHS))
            self.arch = arch
        else:
            self.arch = [arch]

        if isinstance(flags, list):
            self.flags = flags
        else:
            self.flags = [flags]

    def __repr__(self):
        message = '\nCPU requirements:'
        message += '\n-------------------------------------------------------------------'
        message += '\nRequired arch: {}'.format(' or '.join(self.arch))
        message += '\nRequired slots: {}'.format(self.slots)
        message += '\nAllowed overprovision: {}'.format(self.maxOverprovision)
        message += '\nSlots unit: {}'.format("Cores" if self.fullPhysical else "Threads")
        if self.flags:
            message += '\nRequired extension flags: {}'.format(','.join(self.flags))
        return message

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    req = cpurequirements(4, True, flags=['sse2'])
    print(req)
