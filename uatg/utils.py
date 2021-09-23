# See LICENSE.incore for license details

# imports
import os
import glob
import random as rnd
from uatg.log import logger
import ruamel
from ruamel.yaml import YAML


class sv_components:
    """
        This class contains the methods which will return the tb_top and
        interface system verilog tests. This text will be written into 
        SV files.
    """

    def __init__(self, config_file):
        super().__init__()
        self._btb_depth = 32
        config = config_file

        # entries from the aliasing file being read in.
        self.rg_initialize = config['branch_predictor']['register'][
            'bpu_rg_initialize']
        self.rg_allocate = config['branch_predictor']['register'][
            'bpu_rg_allocate']
        self.btb_tag = config['branch_predictor']['wire']['bpu_btb_tag']
        self.btb_entry = config['branch_predictor']['wire']['bpu_btb_entry']
        self.ras_top_index = config['branch_predictor']['wire'][
            'bpu_ras_top_index']
        self.rg_ghr = config['branch_predictor']['register']['bpu_rg_ghr']
        self.valids = config['branch_predictor']['wire']['bpu_btb_tag_valid']
        self.mispredict = config['branch_predictor']['wire'][
            'bpu_mispredict_flag']
        self.bpu_path = config['tb_top']['path_to_bpu']
        self.decoder_path = config['tb_top']['path_to_decoder']
        self.stage0_path = config['tb_top']['path_to_stage0']
        self.fn_decompress_path = config['tb_top']['path_to_fn_decompress']
        self.test = config['test_case']['test']

    # function to generate interface string to be written as interface.sv
    def generate_interface(self):
        """
           returns interface SV syntax. 
        """
        interface = f"interface chromite_intf(input bit CLK,RST_N);\n\t" \
                    f"logic {self.rg_initialize};\n\tlogic [4:0" \
                    f"]{self.rg_allocate};\n"
        interface += f"\n  logic [7:0]{self.rg_ghr};"
        interface += f"\nlogic [{self._btb_depth - 1}:0]{self.valids};"
        interface += f"\n  logic {self.ras_top_index};"
        interface += f"\n  logic [8:0]{self.mispredict};\n"
        for loop_var in range(self._btb_depth):
            interface += f"\n  logic [62:0] {self.btb_tag}_{loop_var};"
        for loop_var in range(self._btb_depth):
            interface += f"\n  logic [67:0] {self.btb_entry}_{loop_var};"
        interface += """\n `include \"coverpoints.sv\"
                  \n  string test = `cnvstr(`TEST);
                  \n\n initial
begin
if(test == \"gshare_fa_mispredict_loop_01\")
  begin
     gshare_fa_mispredict_loop_cg mispredict_cg;
     mispredict_cg=new();
  end
if(test == \"gshare_fa_ghr_zeros_01\" || test == \"gshare_fa_ghr_ones_01\" 
                                   || test == \"gshare_fa_ghr_alternating_01\")
  begin
     bpu_rg_ghr_cg ghr_cg;
     ghr_cg=new();
  end
if(test == \"gshare_fa_fence_01\" || test == \"gshare_fa_selfmodifying_01\")
  begin
    gshare_fa_fence_cg fence_cg;
    fence_cg=new();
  end
if(test == \"gshare_fa_btb_fill_01\")
  begin
    gshare_fa_btb_fill_cg fill_cg;
    fill_cg=new();
  end
if(test == \"regression\")
  begin
   gshare_fa_mispredict_loop_cg mispredict_cg;
   bpu_rg_ghr_cg ghr_cg;
   gshare_fa_fence_cg fence_cg;
   gshare_fa_btb_fill_cg fill_cg;
   mispredict_cg=new();
   ghr_cg=new();
   fill_cg=new();
   fence_cg=new();
  end
end
\n"""
        interface += "\nendinterface\n"

        return interface

    # function to generate tb_top string to be written into tb_top.sv
    def generate_tb_top(self):
        """
          returns tb_top Sv syntax
       """
        tb_top = ("`include \"defines.sv\"\n"
                  "`include \"interface.sv\"\n"
                  "`ifdef RV64\n"
                  "module tb_top(input CLK,RST_N);\n"
                  "  chromite_intf intf(CLK,RST_N);\n"
                  "  mkTbSoc mktbsoc(.CLK(intf.CLK),.RST_N(intf.RST_N));\n"
                  "  always @(posedge CLK)\n"
                  "  begin\n")
        tb_top += f"\tif(!RST_N) begin\n\tintf.{self.rg_initialize} = " \
                  f"{self.bpu_path}.{self.rg_initialize};\n\tintf." \
                  f"{self.rg_allocate} = {self.bpu_path}.{self.rg_allocate};" \
                  f"\n\tintf.{self.ras_top_index} = {self.bpu_path}." \
                  f"{self.ras_top_index};\n\tintf.{self.rg_ghr} = " \
                  f"{self.bpu_path}.{self.rg_ghr};\n\tintf.{self.mispredict}" \
                  f" = {self.bpu_path}.{self.mispredict}; "
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.btb_tag}_{loop_var} " \
                              f"= {self.bpu_path}" \
                              f".self.btb_tag_{loop_var};"
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.btb_entry}_{loop_var} = " \
                              f"{self.bpu_path}.{self.btb_entry}_{loop_var};"
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.valids}[{loop_var}] " \
                              f"= {self.bpu_path}" \
                              f".{self.btb_tag}_{loop_var}[0];"
        tb_top += "\n\tend\n\telse\n\tbegin\n"
        tb_top += f"\tintf.{self.rg_initialize} = {self.bpu_path}" \
                  f".{self.rg_initialize};\n\tintf.{self.rg_allocate} = " \
                  f"{self.bpu_path}.{self.rg_allocate};\n\tintf." \
                  f"{self.ras_top_index} = {self.bpu_path}" \
                  f".{self.ras_top_index};\n\tintf.{self.rg_ghr} = " \
                  f"{self.bpu_path}.{self.rg_ghr};\n\tintf.{self.mispredict}" \
                  f" = {self.bpu_path}.{self.mispredict}; "
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.btb_tag}_ = {self.bpu_path}" \
                              f".{self.btb_tag}_{loop_var};"
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.btb_entry}_{loop_var} = " \
                              f"{self.bpu_path}.{self.btb_entry}_{loop_var};"
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.valids}[{loop_var}] " \
                              f"= {self.bpu_path}" \
                              f".{self.btb_tag}_{loop_var}[0];"
        tb_top = tb_top + """\n\tend
end

`ifdef TRN
initial
begin
  //$recordfile(\"tb_top.trn\");
  //$recordvars();
end
`endif

`ifdef VCS
initial
begin
  //$dumpfile(\"vsim.vcd\");
  //$dumpvars(0,tb_top);
end
`endif

endmoduleNeeded to generate/validate tests
`endif\n"""

        return tb_top

    # generate the defines file to select the tests the user wants to be run
    # on the simulator.
    def generate_defines(self):
        """
        creates the syntax for the defines file which will be used to select 
        tests.
        """
        defines = f"""/// All compile time macros will be defined here

// Macro to indicate the ISA 
`define RV64

//Macro to reset 
`define BSV_RESET_NAME RST_N

//Macro to indicate compressed or decompressed
`define COMPRESSED 

//Macro to indicate the waveform dump
  //for questa 
    `define VCS
  //for cadence 
    `define TRN

//Macro to indicate the test_case
`define cnvstr(x) `\"x`\"
`define TEST {self.test}"""
        return defines


# Utility Functions
def info(version):
    """The function prints the Information about UATG. """
    logger.info('****** μArchitectural Test Generator - UATG *******')
    logger.info(f'Version : {version}')
    logger.info('Copyright (c) 2021, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')


def load_yaml(file):
    """
        Common function to load YAML Files.
        The function checks if the file is of YAML format else exits.
        If the file is in YAML, it reads the file and returns the data from the 
        file as a dictionary.
    """
    if os.path.exists(file) and (file.endswith('.yaml') or
                                 file.endswith('.yml')):
        yaml = YAML(typ="rt")
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        try:
            with open(file, "r") as file:
                return yaml.load(file)
        except ruamel.yaml.constructor.DuplicateKeyError as msg:
            logger.error(f'error: {msg}')
    else:
        logger.error(f'error: {file} is not a valid yaml file')
        exit('INVALID_FILE/PATH')


def combine_config_yamls(configuration_path):
    """
        This function reads all the YAML file paths specified by the user.
        Loads the data into a dictionary and then returns it to the invoking 
        method.
    """
    dut_dict = {}
    try:
        dut_dict['isa_dict'] = load_yaml(configuration_path[0])  # Yaml for ISA
    except IndexError:
        logger.error('isa configuration yaml is missing. '
                     'UATG cannot proceed without '
                     'providing a path to the valid YAML file')
        raise Exception('MISSING_ISA_CONFIG_YAML')
    try:
        dut_dict['core_config'] = load_yaml(
            configuration_path[1])  # Yaml for DUT configuration
    except IndexError:
        logger.error('core config yaml is missing. UATG cannot proceed without '
                     'providing a path to the valid YAML file')
        raise Exception('MISSING_CORE_CONFIGURATION_YAML')
    try:
        dut_dict['rv64i_custom'] = load_yaml(
            configuration_path[2])  # Yaml for Modules
    except IndexError:
        logger.error('rv64i_custom path is missing. UATG cannot proceed '
                     'without providing a path to rv64i_custom.yaml file')
        raise Exception('MISSING_RV64I_CUSTOM')
    try:
        dut_dict['csr_grouping'] = load_yaml(
            configuration_path[3])  # YAML for CSRs
    except IndexError:
        logger.error('Path to csr_grouping.yaml is invalid.')
        raise Exception('MISSING_CSRGROUPING64')

    return (dut_dict)


def join_yaml_reports(work_dir='abs_path_here/', module='branch_predictor'):
    """
        Function that combines all the verification report yaml files into one.
        This function is used as a part of the Check_logs/validate
        option present in UATG.
    """
    files = [
        file for file in os.listdir(os.path.join(work_dir, 'reports', module))
        if file.endswith('_report.yaml')
    ]
    yaml = YAML()
    reports = {}
    for file in files:
        fp = open(os.path.join(work_dir, 'reports', module, file), 'r')
        data = yaml.load(fp)
        reports.update(dict(data))
        fp.close()
    f = open(os.path.join(work_dir, 'combined_reports.yaml'), 'w')
    yaml.default_flow_style = False
    yaml.dump(reports, f)
    f.close()


def create_linker(target_dir):
    """
        Creates a template linker file in the target_directory specified by the 
        user. 
    """

    out = '''OUTPUT_ARCH( "riscv" )
ENTRY(rvtest_entry_point)

SECTIONS
{
  . = 0x80000000;
  .text.init : { *(.text.init) }
  . = ALIGN(0x1000);
  .tohost : { *(.tohost) }
  . = ALIGN(0x1000);
  .text : { *(.text) }
  . = ALIGN(0x1000);
  .data : { *(.data) }
  .data.string : { *(.data.string)}
  .bss : { *(.bss) }
  _end = .;
} 
'''

    with open(os.path.join(target_dir, "link.ld"), 'w') as outfile:
        outfile.write(out)


def create_model_test_h(target_dir):
    """
    Creates a model_test.h file in the target directory specified by the user.
    """
    out = '''#ifndef _COMPLIANCE_MODEL_H
#define _COMPLIANCE_MODEL_H

#define RVMODEL_DATA_SECTION \
        .pushsection .tohost,"aw",@progbits;                            \
        .align 8; .global tohost; tohost: .dword 0;                     \
        .align 8; .global fromhost; fromhost: .dword 0;                 \
        .popsection;                                                    \
        .align 8; .global begin_regstate; begin_regstate:               \
        .word 128;                                                      \
        .align 8; .global end_regstate; end_regstate:                   \
        .word 4;

//RV_COMPLIANCE_HALT
#define RVMODEL_HALT                                              \
shakti_end:                                                             \
      li gp, 1;                                                         \
      sw gp, tohost, t5;                                                \
      fence.i;                                                           \
      li t6, 0x20000;                                                   \
      la t5, begin_signature;                                           \
      sw t5, 0(t6);                                                     \
      la t5, end_signature;                                             \
      sw t5, 8(t6);                                                     \
      sw t5, 12(t6);  

#define RVMODEL_BOOT

//RV_COMPLIANCE_DATA_BEGIN
#define RVMODEL_DATA_BEGIN                                              \
  RVMODEL_DATA_SECTION                                                        \
  .align 4; .global begin_signature; begin_signature:

//RV_COMPLIANCE_DATA_END
#define RVMODEL_DATA_END                                                      \
        .align 4; .global end_signature; end_signature:  

//RVTEST_IO_INIT
#define RVMODEL_IO_INIT
//RVTEST_IO_WRITE_STR
#define RVMODEL_IO_WRITE_STR(_R, _STR)
//RVTEST_IO_CHECK
#define RVMODEL_IO_CHECK()
//RVTEST_IO_ASSERT_GPR_EQ
#define RVMODEL_IO_ASSERT_GPR_EQ(_S, _R, _I)
//RVTEST_IO_ASSERT_SFPR_EQ
#define RVMODEL_IO_ASSERT_SFPR_EQ(_F, _R, _I)
//RVTEST_IO_ASSERT_DFPR_EQ
#define RVMODEL_IO_ASSERT_DFPR_EQ(_D, _R, _I)

#define RVMODEL_SET_MSW_INT \
 li t1, 1;                         \
 li t2, 0x2000000;                 \
 sw t1, 0(t2);

#define RVMODEL_CLEAR_MSW_INT     \
 li t2, 0x2000000;                 \
 sw x0, 0(t2);

#define RVMODEL_CLEAR_MTIMER_INT

#define RVMODEL_CLEAR_MEXT_INT
#endif // _COMPLIANCE_MODEL_H'''

    with open(os.path.join(target_dir, 'model_test.h'), 'w') as outfile:
        outfile.write(out)


def create_plugins(plugins_path):
    """
    This function is used to create Yapsy Plugin files.
    The YAPSY plugins are required to be in a certain pattern. This function 
    will read the test classes and create files complying to the pattern.
    Yapsy will ignore all other python file which does not have a 
    .yapsy-plugin file associated with it.
    """
    files = os.listdir(plugins_path)
    for file in files:
        if ('.py' in file) and (not file.startswith('.')):
            module_name = file[0:-3]
            f = open(os.path.join(plugins_path, module_name + '.yapsy-plugin'),
                     'w')
            f.write("[Core]\nName=" + module_name + "\nModule=" + module_name)
            f.close()


def create_config_file(config_path):
    """
        Creates a template config.ini file at the config_path directory.
        Invoked by running uatg setup.
    """
    cfg = '# See LICENSE.incore for license details\n\n' \
          '[uatg]\n\n# [info, error, debug] set verbosity level to view ' \
          'different levels of messages.\nverbose = info\n# [True, False] ' \
          'the clean flag removes unnecessary files from the previous runs ' \
          'and cleans directories\nclean = False\n\n# Enter the modules whose' \
          ' tests are to be generated/validated in comma separated format.\n' \
          '# Run \'uatg --list-modules -md <path> \' to find all the modules ' \
          'that are supported.\n# Use \'all\' to generate/validate all ' \
          'modules\nmodules = all\n\n# Absolute path to chromite_uatg_tests' \
          '/modules Directory\n' \
          'module_dir = /home/user/myquickstart/chromite_uatg_tests/modules/' \
          '\n\n# Directory to dump assembly files and reports\n' \
          'work_dir = /home/user/myquickstart/work/' \
          '\n\n# location to store the link.ld linker file. By default it\'s ' \
          'same as work_dir\n' \
          'linker_dir = /home/user/myquickstart/work/' \
          '\n\n# Path to the yaml files containing DUT Configuration.\n' \
          'configuration_files = /home/user/myquickstart/isa_config.yaml,'\
          '/home/user/myquickstart/core_config.yaml,' \
          '/home/user/myquickstart/custom_config.yaml,' \
          '/home/user/myquickstart/csr_grouping.yaml' \
          '\n\n# Absolute Path of the yaml file contain' \
          'ing the signal aliases of the DUT ' \
          '\nalias_file = /home/user/myquickstart/chromite_uatg_tests/'\
          'aliasing.yaml' \
          '\n\n# [True, False] If the gen_test_' \
          'list flag is True, the test_list.yaml needed for running tests in ' \
          'river_core are generated automatically.\n# Unless you want to ' \
          'run individual tests in river_core, set the flag to True\n' \
          'gen_test_list = True\n# [True, False] If the gen_test flag is True' \
          ', assembly files are generated/overwritten\ngen_test = True\n# ' \
          '[True, False] If the val_test flag is True, Log from DUT are ' \
          'parsed and the modules are validated\nval_test = False\n# [True' \
          ', False] If the gen_cvg flag is True, System Verilog cover-groups ' \
          'are generated\ngen_cvg = True'

    with open(os.path.join(config_path, 'config.ini'), 'w') as f:
        f.write(cfg)


def create_alias_file(alias_path):
    """
        Creates a template aliasing.yaml file at the alias_path directory.
        Invoked by running uatg setup
    """
    alias = 'tb_top:\n path_to_bpu: ' \
            'mktbsoc.soc.ccore.riscv.stage0.bpu\n path_to_decoder: ' \
            'mktbsoc.soc.ccore.riscv.stage2.instance_decoder_func_32_2\n' \
            ' path_to_stage0: mktbsoc.soc.ccore.riscv.stage0\n ' \
            'path_to_fn_decompress: ' \
            'mktbsoc.soc.ccore.riscv.stage1.instance_fn_decompress_0\n\ntest_' \
            'case:\n test: regression\n\nbranch_predictor:\n input:\n output:' \
            '\n register:\n  bpu_rg_ghr: rg_ghr_port1__read\n  bpu_rg_' \
            'initialize: rg_initialize\n  bpu_rg_allocate: ' \
            'rg_allocate\n wire:\n  bpu_mispredict_flag: ' \
            'ma_mispredict_g\n  bpu_btb_tag: ' \
            'v_reg_btb_tag\n  bpu_btb_entry: ' \
            'v_reg_btb_entry\n  bpu_ras_top_index: ' \
            'ras_stack_top_index_port2__read\n  bpu_btb_tag_valid: ' \
            'btb_valids\n '

    with open(os.path.join(alias_path, 'aliasing.yaml'), 'w') as f:
        f.write(alias)


def create_dut_config_files(dut_config_path):
    """
    Creates a template dut_config.yaml (based on Chromite's default
    configuration at the dut_config_path.
    Invoked by running the uatg setup command
    """

    s2 = ' ' * 2
    s4 = s2 * 2
    s6 = s2 * 3
    s8 = s4 * 2
    rv64i_isa = f'hart_ids: [0]\nhart0:\n{s2}custom_exceptions:\n{s4}- cause' \
                f'_val: 25\n{s4}  cause_name: halt_ebreak\n{s4}  priv_mode: M' \
                f'\n{s4}- cause_val: 26\n{s4}  cause_name: halt_trigger\n{s4}' \
                f'  priv_mode: M\n{s4}- cause_val: 28\n{s4}  cause_name: halt_'\
                f'step\n{s4}  priv_mode: M\n{s4}- cause_val: 29\n' \
                f'{s4}  cause_name: halt_reset\n'\
                f'{s4}  priv_mode: M\n{s2}custom_interrupts:' \
                f'\n{s4}- cause_val: 16\n{s4}  cause_name: debug_interrupt' \
                f'\n{s4}  on_reset_enable: 1\n{s4}  priv_mode : M\n{s2}ISA: ' \
                f'RV64IMACSUZicsr_Zifencei\n{s2}User_Spec_Version: "2.3"' \
                f'\n{s2}pmp_granularity: 1\n{s2}physical_addr_sz: 32\n{s2}' \
                f'supported_xlen:\n{s4}- 64\n'

    with open(os.path.join(dut_config_path, 'isa_config.yaml'), 'w') as f:
        f.write(rv64i_isa)

    rv64i_custom = f'hart_ids: [0]\nhart0:\n  dtim_base:\n{s4}reset-val: 0x0' \
                   f'\n{s4}rv32:\n{s6}accessible: false\n{s4}rv64:\n{s6}' \
                   f'accessible: false\n{s6}type:\n{s8}ro_constant: 0x0\n{s6}' \
                   f'shadow:\n{s6}shadow_type:\n{s6}msb: 63\n{s6}lsb: 0\n{s4}' \
                   f'description: dtim base\n{s4}address: 0x7C3\n{s4}priv_' \
                   f'mode: M\n{s2}itim_base:\n{s4}reset-val: 0x0\n{s4}rv32:' \
                   f'\n{s6}accessible: false\n{s4}rv64:\n{s6}accessible: ' \
                   f'false\n{s6}type:\n{s8}ro_constant: 0x0\n{s6}shadow:' \
                   f'\n{s6}shadow_type:\n{s6}msb: 63\n{s6}lsb: 0\n{s4}' \
                   f'description: dtim base\n{s4}address: 0x7C2\n{s4}priv_' \
                   f'mode: M\n  customcontrol:\n{s4}reset-val: 0x000000000000' \
                   f'0017\n{s4}rv32:\n{s6}accessible: false\n{s4}rv64:\n{s6}' \
                   f'accessible: true\n{s6}ienable:\n{s8}implemented: true' \
                   f'\n{s8}type:\n{s8}{s2}ro_constant: 0x1\n{s8}description:' \
                   f' bit for cache-enable of instruction cache, part of rg_' \
                   f'customcontrol\n{s8}shadow:\n{s8}shadow_type:\n{s8}msb: 0' \
                   f'\n{s8}lsb: 0\n{s6}denable:\n{s8}implemented: true\n{s8}' \
                   f'type:\n{s8}{s2}ro_constant: 0x1\n{s8}description: bit ' \
                   f'for cache-enable of data cache, part of rg_customcontrol' \
                   f'\n{s8}shadow:\n{s8}shadow_type:\n{s8}msb: 1\n{s8}lsb: 1' \
                   f'\n{s6}bpuenable:\n{s8}implemented: true\n{s8}type:\n{s8}' \
                   f'{s2}ro_constant: 0x1\n{s8}description: bit for enabling ' \
                   f'branch predictor unit, part of rg_customcontrol\n{s8}' \
                   f'shadow:\n{s8}shadow_type:\n{s8}msb: 2\n{s8}lsb: 2\n{s6}' \
                   f'arith_excep:\n{s8}implemented: true\n{s8}type:\n{s8}{s2}' \
                   f'ro_constant: 0x0\n{s8}description: bit for enabling ' \
                   f'arithmetic exceptions, part of rg_customcontrol\n{s8}' \
                   f'shadow:\n{s8}shadow_type:\n{s8}msb: 3\n{s8}lsb: 3\n{s6}' \
                   f'debug_enable:\n{s8}implemented: true\n{s8}type:\n{s8}' \
                   f'{s2}ro_constant: 0x1\n{s8}description: bit for enabling ' \
                   f'debugger on the current hart\n{s8}shadow:\n{s8}shadow_' \
                   f'type:\n{s8}msb: 4\n{s8}lsb: 4\n{s6}description: the ' \
                   f'register holds enable bits for arithmetic exceptions, ' \
                   f'branch predictor unit, i-cache, d-cache units\n{s6}' \
                   f'address: 0x800\n{s6}priv_mode: U\n'

    with open(os.path.join(dut_config_path, 'custom_config.yaml'), 'w') as f:
        f.write(rv64i_custom)

    core64 = f'm_extension:\n{s2}mul_stages_in : 1\n{s2}mul_stages_out: 1' \
             f'\n{s2}div_stages : 32\nbranch_predictor:\n{s2}instantiate: ' \
             f'True\n{s2}predictor: gshare\n{s2}btb_depth: 32\n{s2}bht_depth:' \
             f' 512\n{s2}history_len: 8\n{s2}history_bits: 5\n{s2}ras_depth: 8'

    with open(os.path.join(dut_config_path, 'core_config.yaml'), 'w') as f:
        f.write(core64)

    csr_grouping64 = f'grp1:\n{s2}- MISA\n{s2}- MSCRATCH\n{s2}- SSCRATCH' \
                     f'\n{s2}- MVENDORID\n{s2}- MSTATUS\n{s2}- SSTATUS\n{s2}' \
                     f'- MIE\n{s2}- SIE\n{s2}- MIP\n{s2}- SIP\n{s2}- MTVEC' \
                     f'\n{s2}- STVEC\n{s2}- MEPC\n{s2}- SEPC\n{s2}- MCAUSE\n' \
                     f'{s2}- SCAUSE\n{s2}- MTVAL\n{s2}- STVAL\n{s2}- MCYCLE' \
                     f'\n{s2}- MINSTRET\n{s2}- MHARTID\n{s2}- MARCHID\n{s2}' \
                     f'- MIMPID\n{s2}- TIME\n{s2}- CYCLE\n{s2}- MCOUNTINHIBIT' \
                     f'\n{s2}- INSTRET\n{s2}- SATP\n{s2}- MIDELEG\n{s2}' \
                     f'- MEDELEG\n{s2}- PMPCFG0\n{s2}- PMPADDR0\n{s2}' \
                     f'- PMPADDR1\n{s2}- PMPADDR2\n{s2}- PMPADDR3\n{s2}' \
                     f'- CUSTOMCONTROL'
    with open(os.path.join(dut_config_path, 'csr_grouping.yaml'), 'w') as f:
        f.write(csr_grouping64)


def rvtest_data(bit_width=0, num_vals=20, random=True, signed=False, align=4):
    """
    
    Used to specify the data to be loaded into the test_data section of the
    DUT memory. The user will specify the data he wants in this section of the 
    DUT memory.
    """
    size = {
        0: 'word',
        8: 'byte',
        16: 'half',
        32: 'word',
        64: 'dword',
        128: 'quad',
    }
    if bit_width not in size.keys():
        logger.error('bit_width not compatible with byte, half, word or dword')
        exit('BITWIDTH NOT_IN 8,16,32,64')

    data = f'.align {align}\n'
    if bit_width == 0:
        pass
    else:
        max_signed = 2**(bit_width - 1) - 1
        min_signed = -2**(bit_width - 1)
        max_unsigned = 2**bit_width - 1
        min_unsigned = 0
        # data += f'MAX_U:\t.{size[bit_width]} {hex(max_unsigned)}\nMIN_U:\t' \
        #         f'.{size[bit_width]} {hex(min_unsigned)}\n'
        # data += f'MAX_S:\t.{size[bit_width]} {hex(max_signed)}\nMIN_S:\t' \
        #         f'.{size[bit_width]} {hex(min_signed)}\n'
        data += 'RAND_VAL:\n'
        if random:
            for i in range(num_vals):
                if signed:
                    data += f'\t.{size[bit_width]}\t' \
                            f'{hex(rnd.randint(min_signed, max_signed))}\n'
                else:
                    data += f'\t.{size[bit_width]}\t' \
                            f'{hex(rnd.randint(min_unsigned, max_unsigned))}\n'
    data += '\nsample_data:\n.word\t0xbabecafe\n'
    return data


# UATG Functions
def clean_modules(module_dir, modules):
    """
    Function to read the modules specified by the user, check if they exist or
    raise an error. 
    Returns a list of the modules for which tests will be generated.
    """
    module = None
    available_modules = list_of_modules(module_dir)

    if 'all' in modules:

        module = ['all']

    else:
        try:
            modules = modules.replace(' ', ',')
            modules = modules.replace(', ', ',')
            modules = modules.replace(' ,', ',')
            module = list(set(modules.split(",")))
            module.remove('')
            module.sort()

        except ValueError:
            pass
        for element in module:
            if element not in available_modules:
                exit(f'Module {element} is not supported/unavailable.')

    return module


def generate_test_list(asm_dir, uarch_dir, test_list):
    """
      updates the test_list.yaml file with the location of the
      tests generated by test_generator as well the directory to dump the logs.
      Check the test_list format documentation present.
      The test list generation is an optional feature which the user may choose 
      to use. 
    """
    asm_test_list = glob.glob(asm_dir + '/**/*.S')
    env_dir = os.path.join(uarch_dir, 'env/')
    target_dir = asm_dir + '/../'

    for test in asm_test_list:
        logger.debug(f"Current test is {test}")
        base_key = os.path.basename(test)[:-2]
        test_list[base_key] = {}
        test_list[base_key]['generator'] = 'uatg'
        test_list[base_key]['work_dir'] = asm_dir + '/' + base_key
        test_list[base_key]['isa'] = 'rv64imafdc'
        test_list[base_key]['march'] = 'rv64imafdc'
        test_list[base_key]['mabi'] = 'lp64'
        test_list[base_key]['cc'] = 'riscv64-unknown-elf-gcc'
        test_list[base_key][
            'cc_args'] = '-mcmodel=medany -static -std=gnu99 -O2 -fno-common ' \
                         '-fno-builtin-printf -fvisibility=hidden '
        test_list[base_key][
            'linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
        test_list[base_key]['linker_file'] = os.path.join(target_dir, 'link.ld')
        test_list[base_key]['asm_file'] = os.path.join(asm_dir, base_key,
                                                       base_key + '.S')
        test_list[base_key]['include'] = [env_dir, target_dir]
        test_list[base_key]['compile_macros'] = ['XLEN=64']
        test_list[base_key]['extra_compile'] = []
        test_list[base_key]['result'] = 'Unavailable'
    return test_list


def generate_sv_components(sv_dir, alias_file):
    """
    invokes the methods within the sv_components class and creates the sv files.
    tb_top.sv, interface.sv and Defines.sv are created.
    The coverpoints.sv file will be generated by the test_generator
    """
    sv_obj = sv_components(alias_file)
    tb_top = sv_obj.generate_tb_top()
    interface = sv_obj.generate_interface()
    defines = sv_obj.generate_defines()

    with open(os.path.join(sv_dir, "tb_top.sv"), 'w') as tb_top_file:
        tb_top_file.write(tb_top)

    with open(os.path.join(sv_dir, "interface.sv"), 'w') as interface_file:
        interface_file.write(interface)

    with open(os.path.join(sv_dir, "defines.sv"), 'w') as defines_file:
        defines_file.write(defines)


def list_of_modules(module_dir):
    """
    lists the tests modules available by reading the index.yaml file present 
    in the modules directory.
    """
    module_list = []
    if os.path.exists(os.path.join(module_dir, 'index.yaml')):
        modules = load_yaml(os.path.join(module_dir, 'index.yaml'))
        for key, value in modules.items():
            if value is not None:
                module_list.append(key)
        return module_list
    else:
        logger.error(f"index.yaml not found in {module_dir}")
        exit("FILE_NOT_FOUND")
