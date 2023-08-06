if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning pcimatcher unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_pcimatcher.py")

else:
    from pcidev.pcistatus import pcistatus
    from pcidev.pcirequirements import pcirequirements

    def pcimatcher(req: pcirequirements, stat: pcistatus) -> bool:
        return stat.canAllocate(req)
