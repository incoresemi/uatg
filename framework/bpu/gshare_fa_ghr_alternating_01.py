# python script to automate test 11 in micro-arch test
# ghr repeating pattern 010101010....
from yapsy.IPlugin import IPlugin
import regex_formats as rf
import re


class gshare_fa_ghr_alternating_01(IPlugin):

    def __init__(self):
        super().__init__()
        # self.btb_depth = 32
        # self._history_len = 8
        # self.overflow_times = 0
        # self.btb_depth = 32
        self._history_len = 8
        pass

    def execute(self, _bpu_dict):
        _en_bpu = _bpu_dict['instantiate']
        self._history_len = _bpu_dict['history_len']

        if _en_bpu and self._history_len:
            return True
        else:
            return False

    def generate_asm(self, _bpu_dict):
        """
        This function creates assembly code to populate the Global History
        register with alternating 0's and 1's pattern. eg. 010101010....
        history_len = the size of the Global History Register (ghr) in bits.
                      By default history_len is set to be 8 bits.
        The generated assembly code will use the t0 register to alternatively
        enter and exit branches.
        """

        if self.execute(_bpu_dict):
            asm = ".option norvc\n"
            asm = asm + '\taddi t0,x0,1\n'
            asm = asm + '\taddi t1,x0,1\n\taddi t2,x0,2\n\n'
            asm = asm + '\tbeq  t0,x0,lab0\n'

            if self._history_len % 2:
                self._history_len = self._history_len + 1
            # the assembly program is structured in a way that
            # there are odd number of labels.

            for i in range(self._history_len):
                if i % 2:
                    asm = asm + 'lab' + str(i) + ':\n'
                    asm = asm + '\taddi t0,t0,1\n'
                    asm = asm + '\tbeq  t0,x0,lab' + str(i + 1) + '\n'
                else:
                    asm = asm + 'lab' + str(i) + ':\n'
                    asm = asm + '\taddi t0,t0,-1\n'
                    asm = asm + '\tbeq  t0,x0,lab' + str(i + 1) + '\t\n'
            asm = asm + 'lab' + str(self._history_len) + ':\n'
            asm = asm + '\taddi t0,t0,-1\n\n'
            asm = asm + '\taddi t1,t1,-1\n\taddi t2,t2,-1\n'
            asm = asm + '\tbeq  t1,x0,lab0\n\taddi t0,t0,2\n'
            asm = asm + '\tbeq  t2,x0,lab0\n'
            return asm
        else:
            return 0

    def check_log(self, _bpu_dict, log_file_path):
        """
          check if the ghr value is alternating. 
          it should be 01010101 or 10101010 before being fenced 
        """
        if self.execute(_bpu_dict):
            f = open(log_file_path, "r")
            log_file = f.read()
            f.close()

        return None
