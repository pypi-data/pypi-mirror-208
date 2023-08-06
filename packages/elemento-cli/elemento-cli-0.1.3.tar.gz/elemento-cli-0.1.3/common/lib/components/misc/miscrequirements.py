class miscrequirements:
    def __init__(self, os_family, os_flavour=None):
        self.os_family = os_family
        self.os_flavour = os_flavour if os_flavour is not None else os_family
        self.manufacturer = "Apple" if "macos" in os_family.lower() or "darwin" in os_family.lower() else "Any"

    def __repr__(self):
        message = '\nMisc requirements:'
        message += "\nOS family: " + self.os_family
        message += "\nOS flavour: " + self.os_flavour
        message += "\nManufacturer: " + self.manufacturer
        return message

    def __str__(self):
        return self.__repr__()
