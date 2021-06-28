# python program to generate an assembly file which fills the ghr with ones
# the ghr will have a zero entry when the loop exits
from yapsy.IPlugin import IPlugin


class gshare_fa_ghr_ones_01(IPlugin):

    def __init__(self):
        pass

    def generate_asm(self, _bpu_dict):
        '''
        The generated assembly file fills the ghr with ones
        '''

        _en_bpu = _bpu_dict['instantiate']
        _history_len = _bpu_dict['history_len']

        if (_en_bpu and _history_len):
            loop_count = _history_len + 2  # here, 2 is added arbitrarily.
            # it makes sure the loop iterate 2 more times keeping the ghr filled
            # with ones for 2 more predictions

            asm = "\n  addi t0,x0," + str(
                loop_count) + "\n  addi t1,x0,0\n\nloop:\n"
            asm = asm + "  addi t1,t1,1\n  blt t1,t0,loop\n"

            return asm
        else:
            return (0)

    def check_log(self, log_file_path):
        """
          check if all the ghr values are zero throughout the test
        """
        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()
