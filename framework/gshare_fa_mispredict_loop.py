# python program to generate an assembly file which checks if mispredictions occur
# In addition to this, the GHR is also filled with ones (additional test case)
# uses assembly macros

# To-Do -> Create another function which prints the includes and other assembler directives 
#          complying to the test format spec

def gshare_fa_mispredict_loop_01(ghr_width=8):
    '''
    The program creates a simple loop in assembly which checks if 
    mispredictions occur during the warm-up phase of the BPU
    '''

    loop_count = 2*ghr_width # the should iterate atleast 2 times more than the actual ghr width
                             # for the BPU to predict correctly atleast once. We assume 2x arbitrarily
    
    asm = "\n\taddi t0,x0,"+str(loop_count)+"\n\taddi t1,x0,0\n\nloop:\n"
    asm = asm + "\taddi t1,t1,1\n\tblt t1,t0,loop\n"
