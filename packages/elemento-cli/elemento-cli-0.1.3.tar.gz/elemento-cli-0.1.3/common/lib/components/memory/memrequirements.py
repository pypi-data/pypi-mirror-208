class memrequirements:
    def __init__(self, capacity: int = 0, requireECC: bool = False):
        self.capacity = capacity
        self.requireECC = requireECC

    def __repr__(self):
        message = '\nRAM requirements:'
        message += '\n-------------------------------------------------------------------'
        message += '\nRequired capacity (MB): {}'.format(self.capacity)
        message += '\nRequired ECC: {}'.format(self.requireECC)
        return message

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    req = memrequirements(16000, True)
    print(req)
