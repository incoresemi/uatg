# This program generates a assembly code which fills the ghr with zeros
from yapsy.IPlugin import IPlugin


class gshare_fa_ghr_zeros_01(IPlugin):

    def __init__(self):
        self.ghr_width = 8

    def generate_asm(self, _instance):
        '''
          the for loop iterates ghr_width + 2 times printing an 
          assembly program which contains ghr_width + 2 branches which 
          will are *NOT TAKEN*. This fills the ghr with zeros
        '''
        _history_len = _instance['history_len']
        _en_bpu = _instance['instantiate']

        if (_en_bpu and _history_len):
            loop_count = _history_len + 2
            asm = "\n\n## test: gshare_fa_ghr_zeros_01 ##\n\n"
            asm += "  addi t0,x0,1\n"

            for i in range(1, loop_count):
                asm = asm + "branch_" + str(i) + ":\n"
                asm = asm + "  beq t0,x0,branch_" + str(i) + "\n"
                asm = asm + "  addi t0,t0,1\n"

            return (asm)

        else:
            return (0)

    def check_log(self):
        """
          check if all the ghr values are zero throughout the test
        """
