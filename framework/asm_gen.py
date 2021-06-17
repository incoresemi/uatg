## this file creates the final assembly program with the includes and other assembler directoives

from gshare_fa_mispredict_loop import *
from gshare_fa_ghr_alternating import *
from gshare_fa_ghr_zeros import *
from gshare_fa_ghr_ones import *
from gshare_fa_btb_fill import *

## to-do import all functions using syspath or import.utils ....

def asm_gen(select = 0):
    '''
      this function creates the final assembly, which can be run on RiVer.
      The user needs to select the test for which the assembly should be created
      by default, the assembly program for testing misprediction is generated
    '''

    tests = ["gshare_fa_mispredict_loop_01",
             "gshare_fa_ghr_alternating_01",
             "gshare_fa_ghr_zeros_01",
             "gshare_fa_ghr_ones_01",
             "gshare_fa_ghr_alternating_01",
             "gshare_fa_btb_fill_01"]

    asm_header = "#include \"model_test.h\"\n#include \"arch_test.h\"\n"
    asm_header = asm_header + "RVTEST_ISA(\"RV64I\")\n\n"
    asm_header = asm_header + ".section .text.init\n.globl rvtest_entry_point\nrvtest_entry_point:\n"
    asm_header = asm_header + "RVMODEL_BOOT\nRVTEST_CODE_BEGIN\n\n"

    asm_body = globals()[tests[select]]()

    asm_footer = "\nRVTEST_CODE_END\nRVMODEL_HALT\n\nRVTEST_DATA_BEGIN\n.align 4\nrvtest_data:\n"
    asm_footer = asm_footer + ".word 0xbabecafe\nRVTEST_DATA_END\n\nRVMODEL_DATA_BEGIN\nRVMODEL_DATA_END"

    asm = asm_header + asm_body + asm_footer
    return(asm)
