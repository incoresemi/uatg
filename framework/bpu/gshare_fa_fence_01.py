## This program fences the CPU and checks if the BTB entries are invalidated.

from yapsy.IPlugin import IPlugin


class gshare_fa_fence_01(IPlugin):
    """
    This program generates an assembly program which fences the CPU and
    checks if the BTB entries are invalidated
    """

    def __init__(self):
        self.recurse_level = 5

    def generate_asm(self, _bpu_dict):
        """
        This code is derived from the ras_push_pop code. Fence instructions are
        introduced.reg x30 is used as looping variable. reg x31 used as
        a temp variable
        """
        _en_ras = _bpu_dict['ras_depth']
        _en_bpu = _bpu_dict['instantiate']

        if _en_ras and _en_bpu:
            recurse_level = self.recurse_level
            no_ops = "  addi x31,x0,5\n  addi x31,x0,-5\n"
            asm = "  addi x30,x0," + str(recurse_level) + "\n"
            asm = asm + "  call x1,lab1\n  beq  x30,x0,end\n  fence.i\n"

            for i in range(1, recurse_level + 1):
                asm = asm + "lab" + str(i) + ":\n"
                if i == recurse_level:
                    asm = asm + "  fence.i\n  addi x30,x30,-1\n"
                else:
                    asm = asm + no_ops * 3 + "  call x" + str(
                        i + 1) + ", lab" + str(i + 1) + "\n"
                asm = asm + no_ops * 3 + "  ret\n"
            asm = asm + "end:\n  nop\n"

            return asm
        else:
            return (0)

    def check_log(self, log_file_path):
        """
        check if rg_allocate becomes zero ofater encountering fence.
        also check if the valid bits become zero
        and if the ghr becomes zero
        """

        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()
