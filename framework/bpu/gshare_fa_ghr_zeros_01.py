# This program generates a assembly code which fills the ghr with zeros
from yapsy.IPlugin import IPlugin


class gshare_fa_ghr_zeros_01(IPlugin):

    def __init__(self):
        self.ghr_width = 8

    def generate_asm(self, bpu_class):
        '''
          the for loop iterates ghr_width + 2 times printing an 
          assembly program which contains ghr_width + 2 branches which 
          will are *NOT TAKEN*. This fills the ghr with zeros
        '''
        if bpu_class.history_len == 0:
            return None

        loop_count = bpu_class.history_len + 2
        asm = "## test: gshare_fa_ghr_zeros_01\n\n\n\n"
        asm += "  addi t0,x0,1\n"

        for i in range(1, loop_count):
            asm = asm + "branch_" + str(i) + ":\n"
            asm = asm + "  beq t0,x0,branch_" + str(i) + "\n"
            asm = asm + "  addi t0,t0,1\n"

        return (asm)
