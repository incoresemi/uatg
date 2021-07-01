# Python program to generate the self modifying assembly test program

from yapsy.IPlugin import IPlugin
import regex_formats as rf
import re


class gshare_fa_btb_selfmodifying_01(IPlugin):

    def __init__(self):
        super().__init__()
        pass

    def execute(self, _bpu_dict):
        _en_bpu = _bpu_dict['instantiate']
        if _en_bpu:
            return True
        else:
            return False

    def generate_asm(self, _bpu_dict):
        """
          This method returns the asm file.
        """

        asm = ".option norvc\n\n"
        asm += "  addi t3,x0,0\n\taddi t4,x0,3\n\tjal x0,first\n\n"
        asm += "first:\n\taddi t3,t3,1\n\tbeq t3,t4,end\n\tjal x0,first" \
               + "\n\tjal x0,fin\n\n"
        asm += "end:\n\taddi x0,x0,0\n\taddi t0,x0,1\n\tslli t0,t0,31" \
               + "\n\taddi t0,t0,0x3a4\n"
        asm += "\taddi t1,x0,0x33\n\taddi t3,x0,4\n\tsw t1,0(t0)\n\t" \
               + "fence.i\n\tjal x0,first\n\n"
        asm = asm + "fin:\n"

        return asm

    def check_log(self, _bpu_dict, log_file_path):
        """
          check if fence is executed properly. 
          The BTBTags should be invalidated and the rg_allocate should return 0
        """

        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()

        fence_executed_result = re.findall(rf.fence_executed_pattern, log_file)
        if len(fence_executed_result) <= 1:
            # check for execution of more than one fence inst
            return False
        return True
