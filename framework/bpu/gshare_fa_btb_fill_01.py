## this module has a function which generates assembly program to fill the BTB with entries
## there are 33 control insts in the generated program, 1 jump from the includes and 32  in the program
from yapsy.IPlugin import IPlugin


class gshare_fa_btb_fill_01(IPlugin):

    def __init__(self):
        self.btb_depth = 32

    def generate_asm(self):
        '''
          it is assumed that the btb_depth will be a multiple of 4 at all times"
        '''
        btb_depth = self.btb_depth
        asm_start = "  addi t1,x0,0\n  addi t2,x0,1\n\n"
        branch_count = int(btb_depth / 4)
        asm_branch = ""
        asm_jump = "  add t1,t1,t2\n  jal x0,entry_" + str(branch_count +
                                                           1) + "\n\n"
        asm_call = "entry_" + str((2 * branch_count) + 1) + ":\n\n"
        asm_end = "exit:\n\n  addi x0,x0,0\n  add x0,x0,0\n\n"
        for i in range((2 * branch_count) + 2, ((3 * branch_count) + 1)):
            asm_call = asm_call + "  call x1,entry_" + str(i) + "\n"
        asm_call = asm_call + "  j exit\n\n"
        for i in range(1, btb_depth):
            if (i <= branch_count):
                if ((i % 2) == 1):
                    asm_branch = asm_branch + "entry_" + str(i) + ":\n"
                    asm_branch = asm_branch + "  add t1,t1,t2\n  beq t1,t2,entry_" + str(
                        i) + "\n\n"
                else:
                    asm_branch = asm_branch + "entry_" + str(i) + ":\n"
                    asm_branch = asm_branch + "  sub t1,t1,t2\n  beq t1,t2,entry_" + str(
                        i) + "\n\n"
            elif (i > branch_count and i <= 2 * branch_count):
                if ((i % 2) == 1):
                    asm_jump = asm_jump + "entry_" + str(i) + ":\n"
                    asm_jump = asm_jump + "  sub t1,t1,t2\n  jal x0,entry_" + str(
                        i + 1) + "\n  addi x0,x0,0\n\n"
                else:
                    asm_jump = asm_jump + "entry_" + str(i) + ":\n"
                    asm_jump = asm_jump + "  add t1,t1,t2\n  jal x0,entry_" + str(
                        i + 1) + "\n  addi x0,x0,0\n\n"

            else:
                if (i >= 3 * branch_count):
                    break
                asm_call = asm_call + "entry_" + str(i + 1) + ":\n"
                for i in range(2):
                    asm_call = asm_call + "  addi x0,x0,0\n"
                asm_call = asm_call + "  ret\n\n"

        asm = asm_start + asm_branch + asm_jump + asm_call + asm_end
        return (asm)
