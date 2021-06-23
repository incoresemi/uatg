# python program to generate an assembly file which checks if mispredictions occur
# In addition to this, the GHR is also filled with ones (additional test case)
# uses assembly macros

# To-Do -> Create another function which prints the includes and other assembler directives 
#          complying to the test format spec

from yapsy.IPlugin import IPlugin

class gshare_fa_mispredict_loop_01(IPlugin):
    def __init__(self):
        self.ghr_width = 8

    def generate_asm(self):
        '''
        The program creates a simple loop in assembly which checks if 
        mispredictions occur during the warm-up phase of the BPU
        '''
        ghr_width = self.ghr_width
        loop_count = 2*ghr_width # the should iterate atleast 2 times more than the actual ghr width
                                 # for the BPU to predict correctly atleast once. We assume 2x arbitrarily
        
        asm = "\n  addi t0,x0,"+str(loop_count)+"\n  addi t1,x0,0\n\nloop:\n"
        asm = asm + "  addi t1,t1,1\n  blt t1,t0,loop\n"

        return(asm)
