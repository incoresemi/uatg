# python program to generate an assembly file which checks if mispredictions
# occur In addition to this, the GHR is also filled with ones (additional
# test case) uses assembly macros

# To-Do -> Create another function which prints the includes and other
# assembler directives complying to the test format spec

from yapsy.IPlugin import IPlugin


class gshare_fa_mispredict_loop_01(IPlugin):

    def __init__(self):
        super().__init__()
        # self.ghr_width = 8
        pass

    def generate_asm(self, _bpu_dict):
        """
        The program creates a simple loop in assembly which checks if
        mispredictions occur during the warm-up phase of the BPU
        """
        _history_len = _bpu_dict['history_len']
        _en_bpu = _bpu_dict['instantiate']

        if _en_bpu and _history_len:
            loop_count = 4 * _history_len  # the should iterate at least 2
            # times more than the actual ghr width for the BPU to predict
            # correctly at least once. We assume 2x arbitrarily

            asm = "\n  addi t0,x0," + str(
                loop_count) + "\n  addi t1,x0,0\n  addi t2,x0,2\n\nloop:\n"
            asm += "\taddi t1,t1,1\n" \
                + "\taddi t2,t2,10\n\tadd t2,t2,t2\n" \
                + "\taddi t2,t2,-10\n\taddi t2,t2,20\n"\
                + "\tadd t2,t2,t2\n\taddi t2,t2,-10\n"\
                + "\tblt t1,t0,loop\n\n"
            asm += "\tadd t2,t0.t1\n"

            return asm
        else:
            return 0

    def check_log(self, log_file_path):
        """
          check if there is a mispredict atleast once after a BTBHit. 
        """
        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()
