# This program generates a assembly code which fills the ghr with zeros

def gshare_fa_ghr_zeros_01(ghr_width=8):
    '''
      the for loop iterates ghr_width + 2 times printing an 
      assembly program which contains ghr_width + 2 branches which 
      will are *NOT TAKEN*. This fills the ghr with zeros
    '''

    loop_count = ghr_width+2
    
    asm = "  addi t0,x0,1\n"
    
    for i in range (1,loop_count):
        asm = asm + "branch_" + str(i) + ":\n"
        asm = asm + "  beq t0,x0,branch_" + str(i) + "\n"
        asm = asm + "  addi t0,t0,1\n"

    return(asm)
