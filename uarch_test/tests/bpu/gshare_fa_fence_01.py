# This program fences the CPU and checks if the BTB entries are invalidated.

from yapsy.IPlugin import IPlugin
import regex_formats as rf
import re
import configparser


class gshare_fa_fence_01(IPlugin):
    """
    This program generates an assembly program which fences the CPU and
    checks if the BTB entries are invalidated
    """

    def __init__(self):
        super().__init__()
        self.recurse_level = 5

    def execute(self, _bpu_dict):
        _en_ras = _bpu_dict['ras_depth']
        _en_bpu = _bpu_dict['instantiate']
        # TODO why  recursing in the asm test?
        if _en_ras and _en_bpu:
            return True
        else:
            return False

    def generate_asm(self):
        """
        This code is derived from the ras_push_pop code. Fence instructions are
        introduced.reg x30 is used as looping variable. reg x31 used as
        a temp variable
        """
        recurse_level = self.recurse_level
        no_ops = "\taddi x31,x0,5\n  addi x31,x0,-5\n"
        asm = "\taddi x30,x0," + str(recurse_level) + "\n"
        asm = asm + "\tcall x1,lab1\n\tbeq x30,x0,end\n\tfence.i\n"

        for i in range(1, recurse_level + 1):
            asm += "lab" + str(i) + ":\n"
            if i == recurse_level:
                asm += "\tfence.i\n\taddi x30,x30,-1\n"
            else:
                asm = asm + no_ops * 3 + "  call x" + str(
                    i + 1) + ", lab" + str(i + 1) + "\n"
            asm = asm + no_ops * 3 + "\tret\n"
        asm = asm + "end:\n\tnop\n"

        return asm

    def check_log(self, log_file_path):
        """
        check if rg_allocate becomes zero after encountering fence.
        also check if the valid bits become zero
        and if the ghr becomes zero
        """

        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()

        fence_executed_result = re.findall(rf.fence_executed_pattern, log_file)
        if len(fence_executed_result) <= 1:
            # check for execution of more than one fence inst
            return False
        return True
    
    def generate_covergroups(self,config_file):
        """
           returns the covergroups for this test
        """
        #ini_file = /Projects/incorecpu/jyothi.g/micro-arch-tests/example.ini
        config = configparser.ConfigParser()
        config.read(config_file)
        #test = config['test']['test_name']
        rg_initialize = config['signals']['rg_initialize']
        rg_allocate = config['signals']['rg_allocate']
        btb_tag = config['signals']['btb_tag']
        ras_top_index_port2__read = config['signals']['ras_top_index_port2__read']
        port1_read = config['signals']['port1_read']
        sv = "covergroup  gshare_fa_fence_01;
option.per_instance=1;
///coverpoint -rg_initialize should toggle from 0->1
{0}_cp : coverpoint {0} {
   bins {0}_0to1 = (0=>1);}

}
///Coverpoint to check the LSB of v_reg_btb_tax_00 is valid
{1}_cp: coverpoint {1} {
        bins valid = {"+ str(self.btb_depth) + "'b11111111_11111111_11111111_11111111};
}
///coverpoint -  rg_initilaize toggles friom 1->0 2. rg_allocate should become zero 3. v_reg_btb_tag_XX should become 0 (the entire 63bit reg) 4. rg_ghr_port1__read should become zeros. 5. ras_stack_top_index_port2__read should become 0\n".format(rg_initialize,valids)
        for i in range(self.btb_depth):
           sv = sv + "{0}_"+str(i)+": coverpoint {0}{\n
           bins {0}_"+str(i)+"1to0 = (1=>0) iff ({1} == 'b0 && {4}_"+str(i)+" == 'b0 && {2} == 'b0 && {3}== 'b0);}".format(rg_initialize,rg_allocate,port1_read,ras_top_index_port2__read,btb_tag)
        sv = sv + "endgroup"

        return (sv)

