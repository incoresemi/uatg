#python script to automate test 11 in microarch test
#ghr repeating pattern 010101010....
from yapsy.IPlugin import IPlugin

class gshare_fa_ghr_alternating_01(IPlugin):
    def __init__(self):
        self.btb_depth = 32
        self.history_len=8
        self.overflow_times=0
    def generate_asm(self):
        '''
        This function creates assembly code to populate the Global History register
        with alternating 0's and 1's pattern. eg. 010101010....
        history_len = the size of the Global History Register (ghr) in bits.
                      By default history_len is set to be 8 bits.
        overflow_times = number of times to repeatedly apply the pattern after
                         filling the Register. By default overflow_times is set to 0

        The generated assembly code will use the t0 register to alternatively enter
        and exit branches.
        '''
        history_len=self.history_len
        overflow_times=self.overflow_times

        asm = '\taddi t0, x0, 1\t\n'
        asm = asm + '\tbeq  t0, x0, lab0\t\n\taddi t0, t0, -1\t\n'

        for i in range(history_len + overflow_times):
            if(i%2):
                asm += 'lab' + str(i) + ':\n'
                asm += '\taddi t0, t0, 1\t\n'
                asm += '\tbeq  t0, x0, lab'+ str(i+1) +'\t\n'
                asm += '\taddi t0, t0, -1\t\n'
            else:
                asm += 'lab' + str(i) + ':\n'
                asm += '\tbeq  t0, x0, lab'+ str(i+1) +'\t\n'
        asm += 'lab' + str(history_len + overflow_times) + ':\n'
        return(asm)
