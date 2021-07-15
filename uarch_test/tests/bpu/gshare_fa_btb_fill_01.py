# This module has a function which generates assembly program to fill the
# BTB with entries # there are 33 control insts in the generated program,
# 1 jump from the includes and 32  in the program

from yapsy.IPlugin import IPlugin
import regex_formats as rf
import re


class gshare_fa_btb_fill_01(IPlugin):

    def __init__(self):
        super().__init__()
        self._btb_depth = 32
        self.test_created = False

    def execute(self, _bpu_dict):
        _en_bpu = _bpu_dict['instantiate']
        self._btb_depth = _bpu_dict['btb_depth']
        if _en_bpu and self._btb_depth:
            return True
        else:
            return False

    def generate_asm(self):
        """
          it is assumed that the btb_depth will be a multiple of 4 at all times"
        """

        asm_start = "\taddi t1,x0,0\n\taddi t2,x0,1\n\n"
        branch_count = int(self._btb_depth / 4)
        asm_branch = ""
        asm_jump = "\tadd t1,t1,t2\n\tjal x0,entry_" + str(branch_count +
                                                           1) + "\n\n"
        asm_call = "entry_" + str((2 * branch_count) + 1) + ":\n\n"
        asm_end = "exit:\n\n\taddi x0,x0,0\n\tadd x0,x0,0\n\n"
        for j in range((2 * branch_count) + 2, ((3 * branch_count) + 1)):
            asm_call += "\tcall x1,entry_" + str(j) + "\n"
        asm_call += "\tj exit\n\n"
        for i in range(1, self._btb_depth):
            if i <= branch_count:
                if (i % 2) == 1:
                    asm_branch += "entry_" + str(i) + ":\n"
                    asm_branch += "add t1,t1,t2\n\tbeq t1,t2," \
                                  "entry_" + str(i) + "\n\n"
                else:
                    asm_branch += "entry_" + str(i) + ":\n"
                    asm_branch += "sub t1,t1,t2\n\tbeq t1,t2," \
                                  "entry_" + str(i) + "\n\n"
            elif branch_count < i <= 2 * branch_count:
                if (i % 2) == 1:
                    asm_jump += "entry_" + str(i) + ":\n"
                    asm_jump += "\tsub t1,t1,t2\n\tjal x0,entry_" + \
                                str(i + 1) + "\n\taddi x0,x0,0\n\n"
                else:
                    asm_jump += "entry_" + str(i) + ":\n"
                    asm_jump += "\tadd t1,t1,t2\n\tjal x0,entry_" + \
                                str(i + 1) + "\n\taddi x0,x0,0\n\n"

            else:
                if i >= 3 * branch_count:
                    break
                asm_call = asm_call + "entry_" + str(i + 1) + ":\n"
                for j in range(2):
                    asm_call = asm_call + "\taddi x0,x0,0\n"
                asm_call = asm_call + "\tret\n\n"

        asm = asm_start + asm_branch + asm_jump + asm_call + asm_end
        return asm

    def check_log(self, log_file_path):
        """
        check if the rg_allocate register value starts at 0 and traverses
        till 31. This makes sure that the BTB was successfully filled. Also
        check if all the 4 Control instructions are encountered at least once
        This can be checked from the training data -> [      5610] [ 0]BPU :
        Received Training: Training_data........
        """

        f = open(log_file_path, "r")
        log_file = f.read()
        f.close()

        alloc_newind_result = re.findall(rf.alloc_newind_pattern, log_file)
        new_arr = []
        for i in range(len(alloc_newind_result)):
            new_arr.append(alloc_newind_result[i][23:])
        # selecting the pattern "Allocating new index: dd ghr: dddddddd"
        # sorting them and removing duplicates
        new_arr = list(set(new_arr))
        new_arr.sort()
        for i in range(self._btb_depth):
            if str(i) not in new_arr[i]:
                return False
        return True

    def generate_covergroups(self):
        """
           returns the covergroups for this test
        """
        sv = '''covergroup gshare_fa_btb_fill_cg;
option.per_instance=1;
///Coverpoint : reg rg_allocate should change from 0 to `btb_depth -1
rg_allocate_cp : coverpoint rg_allocate[4:0] {
    bins rg_allocate_bin[32] = {[0:31]} iff (rg_initialize == 0);
}
///Coverpoints to check the bits 2 and 3 of the v_reg_btb_entry_XX should contain 01,00,10 and 11 (across the 32 entries)
v_reg_btb_entry_0_cp: coverpoint v_reg_btb_entry_0[3:2]{
    bins v_reg_btb_entry_0_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_1_cp: coverpoint v_reg_btb_entry_1[3:2]{
    bins v_reg_btb_entry_1_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_2_cp: coverpoint v_reg_btb_entry_2[3:2]{
    bins v_reg_btb_entry_2_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_3_cp: coverpoint v_reg_btb_entry_3[3:2]{
    bins v_reg_btb_entry_3_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_4_cp: coverpoint v_reg_btb_entry_4[3:2]{
    bins v_reg_btb_entry_4_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_5_cp: coverpoint v_reg_btb_entry_5[3:2]{
    bins v_reg_btb_entry_5_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_6_cp: coverpoint v_reg_btb_entry_6[3:2]{
    bins v_reg_btb_entry_6_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_7_cp: coverpoint v_reg_btb_entry_7[3:2]{
    bins v_reg_btb_entry_7_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_8_cp: coverpoint v_reg_btb_entry_8[3:2]{
    bins v_reg_btb_entry_8_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_9_cp: coverpoint v_reg_btb_entry_9[3:2]{
    bins v_reg_btb_entry_9_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_10_cp: coverpoint v_reg_btb_entry_10[3:2]{
    bins v_reg_btb_entry_10_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_11_cp: coverpoint v_reg_btb_entry_11[3:2]{
    bins v_reg_btb_entry_11_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_12_cp: coverpoint v_reg_btb_entry_12[3:2]{
    bins v_reg_btb_entry_12_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_13_cp: coverpoint v_reg_btb_entry_13[3:2]{
    bins v_reg_btb_entry_13_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_14_cp: coverpoint v_reg_btb_entry_14[3:2]{
    bins v_reg_btb_entry_14_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_15_cp: coverpoint v_reg_btb_entry_15[3:2]{
    bins v_reg_btb_entry_15_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_16_cp: coverpoint v_reg_btb_entry_16[3:2]{
    bins v_reg_btb_entry_16_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_17_cp: coverpoint v_reg_btb_entry_17[3:2]{
    bins v_reg_btb_entry_17_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_18_cp: coverpoint v_reg_btb_entry_18[3:2]{
    bins v_reg_btb_entry_18_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_19_cp: coverpoint v_reg_btb_entry_19[3:2]{
    bins v_reg_btb_entry_19_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_20_cp: coverpoint v_reg_btb_entry_20[3:2]{
    bins v_reg_btb_entry_20_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_21_cp: coverpoint v_reg_btb_entry_21[3:2]{
    bins v_reg_btb_entry_21_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_22_cp: coverpoint v_reg_btb_entry_22[3:2]{
    bins v_reg_btb_entry_22_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_23_cp: coverpoint v_reg_btb_entry_23[3:2]{
    bins v_reg_btb_entry_23_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_24_cp: coverpoint v_reg_btb_entry_24[3:2]{
    bins v_reg_btb_entry_24_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_25_cp: coverpoint v_reg_btb_entry_25[3:2]{
    bins v_reg_btb_entry_25_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_26_cp: coverpoint v_reg_btb_entry_26[3:2]{
    bins v_reg_btb_entry_26_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_27_cp: coverpoint v_reg_btb_entry_27[3:2]{
    bins v_reg_btb_entry_27_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_28_cp: coverpoint v_reg_btb_entry_28[3:2]{
    bins v_reg_btb_entry_28_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_29_cp: coverpoint v_reg_btb_entry_29[3:2]{
    bins v_reg_btb_entry_29_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_30_cp: coverpoint v_reg_btb_entry_30[3:2]{
    bins v_reg_btb_entry_30_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
v_reg_btb_entry_31_cp: coverpoint v_reg_btb_entry_31[3:2]{
    bins v_reg_btb_entry_31_bin = {'d0,'d1,'d2,'d3} iff (rg_initialize == 0);
}
endgroup
        '''

        return (sv)
