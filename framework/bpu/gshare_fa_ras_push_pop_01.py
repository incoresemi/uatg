#python script to automate test 11 in microarch test

from yapsy.IPlugin import IPlugin


class gshare_fa_ras_push_pop_01(IPlugin):

    def __init__(self):
        self.recurse_level = 5

    def generate_asm(self, bpu_class):
        """
        reg x30 is used as looping variable. reg x31 used as a temp variable
        """
        recurse_level = self.recurse_level
        no_ops = '\taddi x31, x0, 5\n\taddi x31, x0, -5\n'
        asm = '\taddi x30, x0, ' + str(recurse_level) + '\n'
        asm += '\tcall x1, lab1\n\tbeq  x30, x0, end\n'

        for i in range(1, recurse_level + 1):
            asm += 'lab' + str(i) + ':\n'
            if (i == recurse_level):
                asm += '\taddi x30, x30, -1\n'
            else:
                asm += no_ops * 3 + '\tcall x' + str(i + 1) + ', lab' + str(
                    i + 1) + '\n'
            asm += no_ops * 3 + '\tret\n'
        asm += 'end:\n\tnop\n'

        return (asm)
