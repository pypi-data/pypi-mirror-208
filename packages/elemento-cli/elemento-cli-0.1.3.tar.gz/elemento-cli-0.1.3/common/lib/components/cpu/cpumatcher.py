if __name__ == '__main__':
    import os

    print("\n\n======================================================================"
          "\nRunning cpumatcher unittests\n")
    os.system(os.path.dirname(__file__) + "/tests/test_cpumatcher.py")

else:
    from cpu.cpustatus import cpustatus
    from cpu.cpurequirements import cpurequirements

    def cpumatcher(req: cpurequirements, stat: cpustatus) -> bool:

        cpu_ok = stat.cpudesc.arch in req.arch

        cpu_ok &= stat.canAllocate(req)

        for flag in req.flags:
            cpu_ok &= flag.upper().replace("NOW!", "Now!") in stat.cpudesc.extensionFlags

        return cpu_ok
