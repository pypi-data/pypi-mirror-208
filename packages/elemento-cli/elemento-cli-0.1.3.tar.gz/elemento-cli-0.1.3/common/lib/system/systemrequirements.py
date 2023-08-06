import jsonpickle

from components.cpu.cpurequirements import cpurequirements
from components.memory.memrequirements import memrequirements
from components.pcidev.pcirequirements import pcirequirements
from components.misc.miscrequirements import miscrequirements


class systemrequirements:
    def __init__(self,
                 cpureq: cpurequirements,
                 memreq: memrequirements,
                 pcireq: pcirequirements = pcirequirements([]),
                 miscreq: miscrequirements = miscrequirements("Any", None)):
        self.cpu = cpureq
        self.mem = memreq
        self.pci = pcireq
        self.misc = miscreq

    def jsonizeToStr(self):
        return jsonpickle.encode(self).replace(' ', '')

    def jsonizeToBytes(self):
        return str.encode(jsonpickle.encode(self).replace(' ', ''))

    def __repr__(self):
        message = 'System requirements\n==================================================================='
        message += self.cpu.__repr__() + "\n"
        message += self.mem.__repr__() + "\n"
        message += self.pci.__repr__() + "\n"
        message += self.misc.__repr__() + "\n"
        message += '\n==================================================================='
        return message

    def __str__(self):
        return self.__repr__()


def getSystemrequirements(reqjson) -> systemrequirements:
    return jsonpickle.decode(reqjson)
