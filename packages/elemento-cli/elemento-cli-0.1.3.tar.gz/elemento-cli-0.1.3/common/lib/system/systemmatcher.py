from system.systemstatus import systemstatus
from system.systemrequirements import systemrequirements
from components.cpu.cpumatcher import cpumatcher
from components.memory.memmatcher import memmatcher
from components.pcidev.pcimatcher import pcimatcher
from components.misc.miscmatcher import miscmatcher


def systemmatcher(req: systemrequirements, stat: systemstatus) -> bool:
    return (cpumatcher(req.cpu, stat.cpu)
            and memmatcher(req.mem, stat.mem)
            and pcimatcher(req.pci, stat.pci)
            and miscmatcher(req.misc, stat.misc))
