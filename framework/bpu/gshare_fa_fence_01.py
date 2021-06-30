# This program fences the CPU and checks if the BTB entries are invalidated.

from yapsy.IPlugin import IPlugin
import regex_formats as rf
import re


class gshare_fa_fence_01(IPlugin):
    """
    This program generates an assembly program which fences the CPU and
    checks if the BTB entries are invalidated
    """

    def __init__(self):
        super().__init__()
        self.recurse_level = 5

    def generate_asm(self, _bpu_dict):
        """
        This code is derived from the ras_push_pop code. Fence instructions are
        introduced.reg x30 is used as looping variable. reg x31 used as
        a temp variable
        """
        _en_ras = _bpu_dict['ras_depth']
        _en_bpu = _bpu_dict['instantiate']
        #TODO why  recursing in the asm test?
        if _en_ras and _en_bpu:
            recurse_level = self.recurse_level
            no_ops = "\taddi x31,x0,5\n  addi x31,x0,-5\n"
            asm = "\taddi x30,x0," + str(recurse_level) + "\n"
            asm = asm + "\tcall x1,lab1\n\tbeq x30,x0,end\n\tfence.i\n"

            for i in range(1, recurse_level + 1):
                asm += "lab" + str(i) + ":\n"
                if i == recurse_level:
                    asm += "\tfence.i\n\taddi x30,x30,-1\n"
                else:
                    asm = asm + no_ops * 3 + "  call x" + str(
                        i + 1) + ", lab" + str(i + 1) + "\n"
                asm = asm + no_ops * 3 + "\tret\n"
            asm = asm + "end:\n\tnop\n"

            return asm
        else:
            return 0

    def check_log(self, log_file_path):
        """
        check if rg_allocate becomes zero ofater encountering fence.
        also check if the valid bits become zero
        and if the ghr becomes zero
        """

        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()

        fence_executed_result = re.findall(rf.fence_executed_pattern, log_file)
        if len(fence_executed_result) <= 1:
            # check for execution of more than one fence inst
            return "gshare_fa_fence_01 failed"
        return "gshare_fa_fence_01 passed"
