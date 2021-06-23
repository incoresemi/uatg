# python program to generate an assembly file which fills the ghr with ones
# the ghr will have a zero entry when the loop exits
from yapsy.IPlugin import IPlugin

class gshare_fa_ghr_ones_01(IPlugin):
    def __init__(self):
        self.ghr_width = 8

    def generate_asm(self):
        ghr_width = self.ghr_width
        '''
        The generated assembly file fills the ghr with ones
        '''

        loop_count = ghr_width+2 # here, 2 is added arbitrarily.
                                 # it makes sure the loop iterate 2 more times keeping the ghr filled with ones for 2 more predictions

        asm = "\n  addi t0,x0,"+str(loop_count)+"\n  addi t1,x0,0\n\nloop:\n"
        asm = asm + "  addi t1,t1,1\n  blt t1,t0,loop\n"

        return(asm)
