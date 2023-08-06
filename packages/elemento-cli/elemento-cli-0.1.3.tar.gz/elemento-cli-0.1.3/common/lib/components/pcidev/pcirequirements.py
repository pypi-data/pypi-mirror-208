

if __name__ == "__main__":
    import os

    print("\n\n======================================================================"
          "\nRunning pcirequirements unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_pcirequirements.py")


else:
    class pcirequirements:
        def __init__(self, devices: list):
            self.devices = {}

            for dev in devices:
                if dev not in self.devices:
                    self.devices[dev] = 1
                else:
                    self.devices[dev] += 1

        def __repr__(self):
            message = '\nPCI requirements:'
            message += '\n-------------------------------------------------------------------'

            for i, dev in enumerate(self.devices):
                message += "\n{}: {} x {}\n".format(i, self.devices[dev], dev)

            return message

        def __str__(self):
            return self.__repr__()
