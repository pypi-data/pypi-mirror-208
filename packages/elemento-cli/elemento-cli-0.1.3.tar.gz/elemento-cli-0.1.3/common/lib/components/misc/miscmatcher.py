if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning miscmatcher unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_miscmatcher.py")

else:
    from misc.miscstatus import miscstatus
    from misc.miscrequirements import miscrequirements

    def miscmatcher(req: miscrequirements, stat: miscstatus) -> bool:
        return stat.canAllocate(req)
