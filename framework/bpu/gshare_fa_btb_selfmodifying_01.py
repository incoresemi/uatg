## Python program to generate the selfmodifyinf assembly test program

from yapsy.IPlugin import IPlugin


class gshare_fa_btb_selfmodifying_01(IPlugin):

    def generate_asm(self, bpu_class):
        """
          This method returns the asm file.
        """

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
