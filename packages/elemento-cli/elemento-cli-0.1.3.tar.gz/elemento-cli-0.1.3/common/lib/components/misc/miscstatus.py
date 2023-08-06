if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning miscstatus unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_miscstatus.py")

else:
    import subprocess
    from misc.miscrequirements import miscrequirements

    class miscstatus:
        def __init__(self, manufacturer=None):
            if not manufacturer:
                self.manufacturer = None
                try:
                    system_info = subprocess.run("dmidecode -t system".split(), stdout=subprocess.PIPE)
                    for line in system_info.stdout.decode("utf-8").split("\n"):
                        if "Manufacturer: " in line:
                            self.manufacturer = line.replace("Manufacturer: ", '').strip('\t').rstrip('\t').upper()
                except:
                    self.manufacturer = ""
            else:
                self.manufacturer = manufacturer.upper()

            if self.manufacturer:
                self.manufacturer = self.manufacturer.replace(' ', '_')
            else:
                self.manufacturer = ''

        def canAllocate(self, req: miscrequirements):
            return self.manufacturer == req.manufacturer.upper() or req.manufacturer.upper() == "ANY"

        def __repr__(self):
            message = "System manufacturer: {}".format(self.manufacturer.lower().capitalize())
            return message

        def __str__(self):
            return self.__repr__()
