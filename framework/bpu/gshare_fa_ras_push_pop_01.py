# python script to automate test 11 in micro-arch test

from yapsy.IPlugin import IPlugin
import regex_formats as rf
import re


class gshare_fa_ras_push_pop_01(IPlugin):

    def __init__(self):
        super().__init__()
        self.recurse_level = 5

    def execute(self, _bpu_dict):
        _en_ras = _bpu_dict['ras_depth']
        _en_bpu = _bpu_dict['instantiate']

        if _en_ras and _en_bpu:
            return True
        else:
            return False

    def generate_asm(self):
        """
        reg x30 is used as looping variable. reg x31 used as a temp variable
        """

        recurse_level = self.recurse_level
        no_ops = '\taddi x31, x0, 5\n\taddi x31, x0, -5\n'
        asm = '\taddi x30, x0, ' + str(recurse_level) + '\n'
        asm += '\tcall x1, lab1\n\tbeq  x30, x0, end\n'

        for i in range(1, recurse_level + 1):
            asm += 'lab' + str(i) + ':\n'
            if i == recurse_level:
                asm += '\taddi x30, x30, -1\n'
            else:
                asm += no_ops * 3 + '\tcall x' + str(i + 1) + ', lab' + str(
                    i + 1) + '\n'
            asm += no_ops * 3 + '\tret\n'
        asm += 'end:\n\tnop\n'
        return asm

    def check_log(self, log_file_path):
        """
        check for pushes and pops in this file. There should be 8 pushes and
        4 pops
        TODO: (should check why that happens, there should be 8pops)
        """

        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()

        pushing_to_ras_result = re.findall(rf.pushing_to_ras_pattern, log_file)
        choosing_top_ras_result = re.findall(rf.choosing_top_ras_pattern,
                                             log_file)
        if len(pushing_to_ras_result) != 8 and \
                len(choosing_top_ras_result) != 4:
            return False

        return True
