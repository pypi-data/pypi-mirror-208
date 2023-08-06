from psutil import virtual_memory
import subprocess


def isECCAvailable():
    try:
        dmidecodeECC = "dmidecode --type 16"
        process = subprocess.Popen(dmidecodeECC.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        return bool("ECC" in output.decode("utf-8"))
    except:
        return False

class memdescriptor:
    def __init__(self):
        self.capacity = virtual_memory().total / 2**20
        self.isECC = isECCAvailable()

    def __repr__(self):
        message = ''
        message += 'Capacity: {}'.format(self.capacity)
        message += '\nIs ECC: {}'.format(self.isECC)
        return message

    def __str__(self):
        return self.__repr__()


if __name__ == '__main__':
    desc = memdescriptor()
    print(desc)
