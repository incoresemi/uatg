# This program generates a assembly code which fills the ghr with zeros
from yapsy.IPlugin import IPlugin

class gshare_fa_ghr_zeros(IPlugin):
    
    def __init__(self):
        self.ghr_width = 8

    
    def generate_asm(self):
        '''
          the for loop iterates ghr_width + 2 times printing an 
          assembly program which contains ghr_width + 2 branches which 
          will are *NOT TAKEN*. This fills the ghr with zeros
        '''
        ghr_width = self.ghr_width
        loop_count = ghr_width+2
        
        asm = "  addi t0,x0,1\n"
        
        for i in range (1,loop_count):
            asm = asm + "branch_" + str(i) + ":\n"
            asm = asm + "  beq t0,x0,branch_" + str(i) + "\n"
            asm = asm + "  addi t0,t0,1\n"

        return(asm)
