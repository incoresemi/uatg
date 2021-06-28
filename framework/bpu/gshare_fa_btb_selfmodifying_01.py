## Python program to generate the selfmodifyinf assembly test program

from yapsy.IPlugin import IPlugin


class gshare_fa_btb_selfmodifying_01(IPlugin):

    def __init__(self):
        pass

    def generate_asm(self, _bpu_dict):
        """
          This method returns the asm file.
        """
        _en_bpu = _bpu_dict['instantiate']

        if (_en_bpu):
            asm = ".option norvc\n\n"
            asm = asm + "  addi t3,x0,0\n\taddi t4,x0,3\n\tjal x0,first\n\n"
            asm = asm + "first:\n\taddi t3,t3,1\n\tbeq t3,t4,end\n\tjal x0,first" \
                  + "\n\tjal x0,fin\n\n"
            asm = asm + "end:\n\taddi x0,x0,0\n\taddi t0,x0,1\n\tslli t0,t0,31" \
                  + "\n\taddi t0,t0,0x3a4\n"
            asm = asm + "\taddi t1,x0,0x33\n\taddi t3,x0,4\n\tsw t1,0(t0)\n\t" \
                  + "fence.i\n\tjal x0,first\n\n"
            asm = asm + "fin:\n"

            return asm
        else:
            return (0)

    def check_log(self, log_file_path):
        """
          check if fence is executed properly. 
          The BTBTags should be invalidated and the rg_allocate should return to 0
        """

        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()
