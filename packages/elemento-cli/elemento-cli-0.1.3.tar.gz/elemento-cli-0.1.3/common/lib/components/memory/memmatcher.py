if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning memmatcher unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_memmatcher.py")

else:
    from memory.memstatus import memstatus
    from memory.memrequirements import memrequirements

    def memmatcher(req: memrequirements, stat: memstatus) -> bool:
        return stat.canAllocate(req)
