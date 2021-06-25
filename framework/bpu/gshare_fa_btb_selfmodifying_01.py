## Python program to generate the selfmodifyinf assembly test program

from yapsy.IPlugin import IPlugin


class gshare_fa_btb_selfmodifying_01(IPlugin):

    def generate_asm(self, bpu_class):
        '''
          This method returns the asm file.
        '''

        asm = ".option norvc\n\n"
        asm = asm + "  addi t3,x0,0\n  addi t4,x0,3\n  jal x0,first\n\n"
        asm = asm + "first:\n  addi t3,t3,1\n  beq t3,t4,end\n  jal x0,first\n  jal x0,fin\n\n"
        asm = asm + "end:\n  addi x0,x0,0\n  addi t0,x0,1\n  slli t0,t0,31\n  addi t0,t0,0x3a4\n"
        asm = asm + "  addi t1,x0,0x33\n  addi t3,x0,4\n  sw t1,0(t0)\n  fence.i\n  jal x0,first\n\n"
        asm = asm + "fin:\n"

        return (asm)
