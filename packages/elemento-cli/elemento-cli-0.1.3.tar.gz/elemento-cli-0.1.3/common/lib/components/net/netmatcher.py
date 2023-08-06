if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning netmatcher unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_netmatcher.py")

else:
    from net.netstatus import netstatus
    from net.netrequirements import netrequirements

    def netmatcher(req: netrequirements, stat: netstatus) -> bool:
        return stat.canAllocate(req)