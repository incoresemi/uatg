# See LICENSE.incore for license details
import re
from glob import glob
from os import remove, listdir, getcwd, chdir
from os.path import join, abspath, exists, basename, dirname
from random import randint
from re import findall, M
from shlex import split
from subprocess import run, PIPE, CalledProcessError

from ruamel.yaml import YAML

from uatg.log import logger


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
    logger.info('****** Micro-Architectural Test Generator - UATG *******')
    logger.info(f'Version : {version}')
    logger.info('Copyright (c) 2021, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')


def uatg_exit():
    logger.info(f'Exiting UATG')
    logger.info(f'Good day! Stay Hydrated.')


def load_yaml(file):
    """
        Common function to load YAML Files.
        The function checks if the file is of YAML format else exits.
        If the file is in YAML, it reads the file and returns the data from the
        file as a dictionary.
    """
    if exists(file) and (file.endswith('.yaml') or file.endswith('.yml')):
        yaml = YAML(typ="rt")
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        try:
            with open(file, "r") as file:
                return yaml.load(file)
        except KeyError:
            logger.error(f'Error Loading YAML')
    else:
        logger.error(f'error: {file} is not a valid yaml file')
        exit('INVALID_FILE/PATH')


def combine_config_yamls(configuration):
    """
        This function reads all the YAML file paths specified by the user.
        Loads the data into a dictionary and then returns it to the invoking
        method.
    """
    dut_dict = {}
    try:
        dut_dict['isa_dict'] = load_yaml(configuration['isa'])  # Yaml for ISA
    except KeyError:
        logger.error('isa configuration yaml is missing. '
                     'UATG cannot proceed without '
                     'providing a path to the valid YAML file')
        raise Exception('MISSING_ISA_CONFIG_YAML')
    try:
        dut_dict['core_config'] = load_yaml(
            configuration['core'])  # Yaml for DUT configuration
    except KeyError:
        logger.error('core config yaml is missing. UATG cannot proceed without '
                     'providing a path to the valid YAML file')
        raise Exception('MISSING_CORE_CONFIGURATION_YAML')
    try:
        dut_dict['rv64i_custom'] = load_yaml(
            configuration['custom'])  # Yaml for Modules
    except KeyError:
        logger.error('custom_config.yaml path is missing. UATG cannot proceed '
                     'without providing a path to the YAMLfile')
        raise Exception('MISSING_CUSTOM_CONFIGURATION_YAML')
    try:
        dut_dict['csr_grouping'] = load_yaml(
            configuration['csr_grouping'])  # YAML for CSRs
    except KeyError:
        logger.error('Path to csr_grouping.yaml is invalid.')
        raise Exception('MISSING_CSRGROUPING')

    try:
        dut_dict['rv64_debug'] = load_yaml(
            configuration['debug'])  # YAML for CSRs
    except KeyError:
        logger.error('Path to rv_debug.yaml is invalid.')
        raise Exception('MISSING_RV_DEBUG')

    return dut_dict


def join_yaml_reports(work_dir='abs_path_here/', module='branch_predictor'):
    """
        Function that combines all the verification report yaml files into one.
        This function is used as a part of the Check_logs/validate
        option present in UATG.
    """
    files = [
        file for file in listdir(join(work_dir, 'reports', module))
        if file.endswith('_report.yaml')
    ]
    yaml = YAML()
    reports = {}
    for file in files:
        fp = open(join(work_dir, 'reports', module, file), 'r')
        data = yaml.load(fp)
        reports.update(dict(data))
        fp.close()
    f = open(join(work_dir, 'combined_reports.yaml'), 'w')
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

    with open(join(target_dir, "link.ld"), 'w') as outfile:
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

    with open(join(target_dir, 'model_test.h'), 'w') as outfile:
        outfile.write(out)


def create_plugins(plugins_path, index_yaml, module):
    """
    This function is used to create Yapsy Plugin files.
    The YAPSY plugins are required to be in a certain pattern. This function
    will read the test classes and create files complying to the pattern.
    Yapsy will ignore all other python file which does not have a
    .yapsy-plugin file associated with it.
    """
    index_yaml = abspath(index_yaml)
    if exists(index_yaml) and (index_yaml.endswith('.yaml') or
                               index_yaml.endswith('.yml')):
        index_yaml = load_yaml(index_yaml)
        logger.debug('using index.yaml from path specified in config.ini file')

    else:
        # the index yaml is in the modules directory
        index_yaml = load_yaml(join(plugins_path, '../index.yaml'))
        logger.debug('using the default index.yaml file ')

    files = listdir(plugins_path)

    for file in files:
        if ('.py' in file) and (not file.startswith('.')):
            test_name = file[0:-3]

            val = False

            try:
                val = index_yaml[module][test_name]
            except KeyError:
                logger.critical(f'There is no entry for test - {test_name}')
                exit(f'update the index.yaml with your new test')

            if val:
                f = open(join(plugins_path, test_name + '.yapsy-plugin'), 'w')
                f.write("[Core]\nName=" + test_name + "\nModule=" + test_name)
                f.close()
                logger.debug(f'Created plugin for {test_name}')
            else:
                try:
                    remove(join(plugins_path, test_name + '.yapsy-plugin'))
                    logger.warn(
                        f'removing already existing plugin file for {test_name}'
                    )
                except FileNotFoundError:
                    logger.debug(f'no plugin for {test_name} to remove')
                    pass
                logger.warn(
                    f'Skippping test {test_name} as index yaml has False')


def create_config_file(config_path, jobs, modules, module_dir, work_dir,
                       linker_dir, alias_path, test_compile, cfg_files):
    """
        Creates a template config.ini file at the config_path directory.
        Invoked by running uatg setup.
    """
    work_dir = '/home/user/myquickstart/work/' if work_dir is None else work_dir

    cfg_files = f'[uatg.configuration_files]\nisa = {cfg_files[0]}\n' \
                f'core = {cfg_files[1]}\ncustom = {cfg_files[2]}\n' \
                f'csr_grouping = {cfg_files[3]}\ndebug = {cfg_files[4]}'

    modules = 'all' if modules is None else modules
    module_dir = '/home/user/myquickstart/chromite_uatg_tests/modules/' \
        if module_dir is None else module_dir

    linker_dir = '/home/user/myquickstart/chromite_uatg_tests/target' \
        if linker_dir is None else linker_dir

    alias_path = '/home/user/myquickstart/chromite_uatg_tests/' \
        if alias_path is None else alias_path

    cfg = '# See LICENSE.incore for license details\n\n' \
          '[uatg]\n\n' \
          '# number of processes to spawn. Default = 1\n' \
          f'jobs = {jobs}\n' \
          '\n# [info, error, debug] set verbosity level to view ' \
          'different levels of messages. ' \
          '\nverbose = info\n\n# [True, False] ' \
          'the clean flag removes unnecessary files from the previous runs ' \
          'and cleans directories\nclean = False\n\n# Enter the modules whose' \
          ' tests are to be generated/validated in comma separated format.\n' \
          '# Run \'uatg --list-modules -md <path> \' to find all the modules ' \
          'that are supported.\n# Use \'all\' to generate/validate all ' \
          f'modules\nmodules = {modules}\n\n' \
          f'\n# Absolute path to chromite_uatg_tests/modules Directory\n' \
          f'module_dir = {module_dir}' \
          '\n\n# Directory to dump assembly files and reports\n' \
          f'work_dir = {work_dir}' \
          '\n\n# location to store the link.ld linker file. By default it\'s ' \
          'the target directory within chromite_uatg_tests\n' \
          f'linker_dir = {linker_dir}' \
          '\n\n# Absolute Path of the yaml file containing the signal ' \
          'aliases of the DUT ' \
          f'\nalias_file = {alias_path}\n\n# path to the index file ' \
          f'containing  the list of tests to be generated. By default, \n' \
          f'# or when empty, UATG will use the index.yaml file within ' \
          f' the modules directory\nindex_file =\n\n' \
          f'# paging modes in for which the tests need to be generated\n' \
          'paging_modes = \n\n' \
          f'# [True, False] If the gen_test_' \
          'list flag is True, the test_list.yaml needed for running tests in ' \
          'river_core are generated automatically.\n# Unless you want to ' \
          'run individual tests in river_core, set the flag to True\n' \
          'gen_test_list = True\n# [True, False] If the gen_test flag is True' \
          ', assembly files are generated/overwritten\ngen_test = True\n# ' \
          '[True, False] If the val_test flag is True, Log from DUT are ' \
          'parsed and the modules are validated\nval_test = False\n# [True' \
          ', False] If the gen_cvg flag is True, System Verilog cover-groups ' \
          f'are generated\ngen_cvg = False\n\ntest_compile = {test_compile}' \
          '\n\n# Path to the yaml files containing DUT Configuration.\n' \
          '# If you are using the CHROMITE core, uncomment the following line' \
          ' by removing the \'#\'.\n# By doing this, UATG will use the ' \
          'checked YAMLs of Chromite\n' \
          '#[uatg.configuration_files]\n' \
          '#isa = /home/user/myquickstart/chromite/build/' \
          'rv64i_isa_checked.yaml \n' \
          '#core = /home/user/myquickstart/chromite/build/core64_checked.yaml' \
          '\n#custom = /home/user/myquickstart/chromite/build/rv64i_custom_' \
          'checked.yaml\n#csr_grouping = /home/user/myquickstart/chromite/' \
          'sample_config/rv64imacsu/csr_grouping64.yaml\n#debug = /home/user/' \
          'myquickstart/chromite/build/rv64i_debug_checked.yaml\n\n# comment ' \
          'the following line by adding a \'#\' in front if you are using ' \
          f'the checked YAMLs from CHROMITE\n\n{cfg_files}'

    with open(join(config_path, 'config.ini'), 'w') as f:
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

    with open(join(alias_path, 'aliasing.yaml'), 'w') as f:
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
                f'  priv_mode: M\n{s4}- cause_val: 28\n{s4}  cause_name: ' \
                f'halt_step\n{s4}  priv_mode: M\n{s4}- cause_val: 29\n' \
                f'{s4}  cause_name: halt_reset\n' \
                f'{s4}  priv_mode: M\n{s2}custom_interrupts:' \
                f'\n{s4}- cause_val: 16\n{s4}  cause_name: debug_interrupt' \
                f'\n{s4}  on_reset_enable: 1\n{s4}  priv_mode : M\n{s2}ISA: ' \
                f'RV64IMACSUZicsr_Zifencei\n{s2}User_Spec_Version: "2.3"' \
                f'\n{s2}pmp_granularity: 1\n{s2}physical_addr_sz: 32\n{s2}' \
                f'supported_xlen:\n{s4}- 64\n'

    with open(join(dut_config_path, 'isa_config.yaml'), 'w') as f:
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

    with open(join(dut_config_path, 'custom_config.yaml'), 'w') as f:
        f.write(rv64i_custom)

    core64 = f'm_extension:\n{s2}mul_stages_in : 1\n{s2}mul_stages_out: 1' \
             f'\n{s2}div_stages : 32\nbranch_predictor:\n{s2}instantiate: ' \
             f'True\n{s2}predictor: gshare\n{s2}btb_depth: 32\n{s2}bht_depth:' \
             f' 512\n{s2}history_len: 8\n{s2}history_bits: 5\n{s2}ras_depth: 8'

    with open(join(dut_config_path, 'core_config.yaml'), 'w') as f:
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
    with open(join(dut_config_path, 'csr_grouping.yaml'), 'w') as f:
        f.write(csr_grouping64)

    rv_debug = f''

    with open(join(dut_config_path, 'rv_debug.yaml'), 'w') as f:
        f.write(rv_debug)


def rvtest_data(bit_width=0, num_vals=20, random=True, signed=False, align=4) \
        -> str:
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
        max_signed = 2 ** (bit_width - 1) - 1
        min_signed = -2 ** (bit_width - 1)
        max_unsigned = 2 ** bit_width - 1
        min_unsigned = 0
        # data += f'MAX_U:\t.{size[bit_width]} {hex(max_unsigned)}\nMIN_U:\t' \
        #         f'.{size[bit_width]} {hex(min_unsigned)}\n'
        # data += f'MAX_S:\t.{size[bit_width]} {hex(max_signed)}\nMIN_S:\t' \
        #         f'.{size[bit_width]} {hex(min_signed)}\n'
        data += 'DATA_SEC:\n'
        if random:
            for i in range(num_vals):
                if signed:
                    data += f'\t.{size[bit_width]}\t' \
                            f'{hex(randint(min_signed, max_signed))}\n'
                else:
                    data += f'\t.{size[bit_width]}\t' \
                            f'{hex(randint(min_unsigned, max_unsigned))}\n'
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

        module = available_modules

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


def find_instances(string, character):
    """
    The function returns all the indices of the
    character present in the string.
    A list is returned
    """
    return [index for index, letter in enumerate(string) if letter == character]


def split_isa_string(isa_string):
    """
    The function parses the ISA string,
    removes the 'S,U,H and N' characters from it.
    The updates ISA string is returned.
    """

    str_match = findall(r'([^\d]*?)(?!_)*(Z.*?)*(_|$)', isa_string, M)
    extension_list = []
    for match in str_match:
        stdisa, z, ignore = match
        if stdisa != '':
            for e in stdisa:
                extension_list.append(e)
        if z != '':
            extension_list.append(z)

    return extension_list


def generate_test_list(asm_dir, uarch_dir, isa, test_list, compile_macros_dict):
    """
      updates the test_list.yaml file with the location of the
      tests generated by test_generator as well the directory to dump the logs.
      Check the test_list format documentation present.
      The test list generation is an optional feature which the user may choose
      to use.
    """
    asm_test_list = glob(asm_dir + '/**/*.S')
    env_dir = join(uarch_dir, 'env/')
    target_dir = abspath(asm_dir + '/../')

    extension_list = split_isa_string(isa)
    march = ''
    if 'rv32' in isa.lower():
        march += 'rv32i'
        xlen = 32
        mabi = 'ilp32'
    elif 'rv64' in isa.lower():
        march += 'rv64i'
        xlen = 64
        mabi = 'lp64'
    if 'M' in extension_list:
        march += 'm'
    if 'A' in extension_list:
        march += 'a'
    if 'F' in extension_list:
        march += 'f'
    if 'D' in extension_list:
        march += 'd'
    if 'C' in extension_list:
        march += 'c'

    for test in asm_test_list:
        logger.debug(f"Current test is {test}")
        base_key = basename(test)[:-2]
        test_list[base_key] = {}
        test_list[base_key]['generator'] = 'uatg'
        test_list[base_key]['work_dir'] = abspath(asm_dir + '/' + base_key)
        test_list[base_key]['isa'] = isa
        test_list[base_key]['march'] = march
        test_list[base_key]['mabi'] = mabi
        test_list[base_key]['cc'] = f'riscv{xlen}-unknown-elf-gcc'
        test_list[base_key][
            'cc_args'] = '-mcmodel=medany -static -std=gnu99 -O2 -fno-common ' \
                         '-fno-builtin-printf -fvisibility=hidden '
        test_list[base_key][
            'linker_args'] = '-static -nostdlib -nostartfiles -lm -lgcc -T'
        test_list[base_key]['linker_file'] = abspath(join(
            target_dir, 'link.ld'))
        test_list[base_key]['asm_file'] = abspath(
            join(asm_dir, base_key, base_key + '.S'))
        test_list[base_key]['include'] = [env_dir, target_dir]
        test_list[base_key]['compile_macros'] = compile_macros_dict[base_key]
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

    with open(join(sv_dir, "tb_top.sv"), 'w') as tb_top_file:
        tb_top_file.write(tb_top)

    with open(join(sv_dir, "interface.sv"), 'w') as interface_file:
        interface_file.write(interface)

    with open(join(sv_dir, "defines.sv"), 'w') as defines_file:
        defines_file.write(defines)


def list_of_modules(module_dir):
    """
    lists the tests modules available by reading the index.yaml file present
    in the modules directory.
    """
    module_list = []
    if exists(join(module_dir, 'index.yaml')):
        modules = load_yaml(join(module_dir, 'index.yaml'))
        for key, value in modules.items():
            if value is not None:
                module_list.append(key)
        return module_list
    else:
        logger.error(f"index.yaml not found in {module_dir}")
        exit("FILE_NOT_FOUND")


def dump_makefile(isa, link_path, test_path, test_name, env_path, work_dir,
                  compile_macros):
    compiler = 'riscv64-unknown-elf-gcc'
    mcmodel = 'medany'
    mabi = 'lp64'
    march = isa.lower()[:8]
    macros = ''

    if compile_macros:
        macros = '-D' + ' -D'.join(compile_macros)

    flags = '-static -std=gnu99 -O2 -fno-common -fno-builtin-printf ' \
            '-fvisibility=hidden -static -nostdlib -nostartfiles -lm -lgcc'
    cmd = f'{compiler} -mcmodel={mcmodel} {flags} -march={march} -mabi={mabi}' \
          f' -lm -lgcc -T {join(link_path, "link.ld")} {test_path}' \
          f' -I {env_path}' \
          f' -I {work_dir} {macros}' \
          f' -o /dev/null'

    return cmd


def setup_pages(pte_dict,
                page_size=4096,
                paging_mode='sv39',
                valid_ll_pages=64,
                mode='machine',
                megapage=False,
                gigapage=False,
                terapage=False,
                petapage=False,
                user_superpage=False,
                user_supervisor_superpage=False,
                fault=False,
                mem_fault=False,
                misaligned_superpage=False,
                mstatus_sum_bit=False,
                mstatus_mxr_bit=False):
    """
        Sets up pages using Assembly to run tests in User and Supervisor modes.
        More documentation can be found in the Paging Modes section of UATG's 
        documentation.

        :param pte_dict: Dictionary containing information about the PTE bits in LL pages.
        :param page_size: Size of the pages (default - 4KiB)
        :param paging_mode: Paging mode used in the tests ( default - sv39)
        :param valid_ll_pages: Valid last level pages to be created.
        :param mode: Mode of execution for which the test is being generated.
        :param megapage: True when a megapage is to be created.
        :param gigapage: True when a gigapage is to be created.
        :param terapage: True when a terapage is to be created.
        :param petapage: True when a petapage is to be created.
        :param user_superpage: True when user superpage is to be created.
        :param user_supervisor_superpage: True when user as well as supervisor superpage is to be generated.
        :param fault: True when the test is supposed to create a fault.
        :param mem_fault: True when the test creates a virtual memory fault.
        :param misaligned_superpage: True when a misaligned superpage (fault) is to be created
        :param mstatus_mxr_bit: True when the MSTATUS.MXR bit is to be set
        :param mstatus_sum_bit: True when the MSTATUS.SUM bit is to be set
        
        :type pte_dict: dict
        :type page_size: int
        :type paging_mode: str
        :type valid_ll_pages: int
        :type mode: str
        :type megapage: bool
        :type gigapage: bool
        :type terapage: bool
        :type petapage: bool
        :type user_superpage: bool
        :type user_supervisor_superpage: bool
        :type fault: bool
        :type mem_fault: bool
        :type misaligned_superpage: bool
        :type mstatus_mxr_bit: bool
        :type mstatus_sum_bit: bool

        :returns: ([out_code_string], out_data_string)
        :rtype: tuple(list, str)
    """

    if mode == 'machine':
        # machine mode tests don't have anything to do with pages.
        # so, we return a list of empty strings.
        # currently there are 5 elements which is appended into the first 
        # list when it is returned, hence the default list also has 5 elements.
        return ['', '', '', '', ''], ''

    # a default PTE bit dictionary to use when the test plugin fails to provide one
    # a fair assumption that all bits will be true is made.
    # a test plugin would return an updated dictionary when it intends to create a fault
    if pte_dict is None:
        pte_dict = {
            'valid': True,
            'read': True,
            'write': True,
            'execute': True,
            'user': True if mode=='user' else False,
            'globl': True,
            'access': True,
            'dirty': True
        }

    # number of entries in one pagetable 
    # (for sv39 and above, 512 entries since there are 8 bytes per PTE in a 4KiB page)
    # in the case of sv32, there will 2x the number of entries as the PTE is 4 bytes.
    entries_per_pt = page_size // 8

    # assuming that the size will always be a power of 2
    power = len(bin(page_size)[2:]) - 1
    align = power
    #shift_amount = 60
    levels, mode_val = None, None

    # assuming default xlen is 64
    xlen = 64

    # creating a dictionary with all required values based on paging mode
    # to avoid if..elif..else ladders
    # most values used here are obtained/inferred from the RISC-V privileged specification.
    paging_val_dict = {
            'sv32': {
                'satp_mode_val': 1,
                'levels' : 2,
                'superpage_level' : {
                    'megapage' : 1
                    },
                'entries' : entries_per_pt * 2,
                'shift_amount' : 31,
                'xlen' : 32,
                'paging_offset_constant' : "0x0"
                },

            'sv39': {
                'satp_mode_val' : 8,
                'levels' : 3,
                'superpage_level' : {
                    'megapage' : 2,
                    'gigapage' : 1
                    },
                'entries' : entries_per_pt,
                'shift_amount' : 60,
                'xlen': 64,
                'paging_offset_constant' : "0x1e0"
                },

            'sv48': {
                'satp_mode_val' : 9,
                'levels' : 4,
                'superpage_level' : {
                    'megapage' : 3,
                    'gigapage' : 2,
                    'terapage' : 1
                    },
                'entries' : entries_per_pt,
                'shift_amount' : 60,
                'xlen' : 64,
                'paging_offset_constant' : "0xF0"
                },
            
            'sv57': {
                'satp_mode_val': 10,
                'levels' : 5,
                'superpage_level' : {
                    'megapage' : 4,
                    'gigapage' : 3,
                    'terapage' : 2,
                    'petapage' : 1
                    },
                'entries' : entries_per_pt,
                'shift_amount' : 60,
                'xlen' : 64,
                'paging_offset_constant' : "0x78"
                }
            }
    
    # selecting the largest superpage possible based on the paging mode
    if petapage == True and paging_mode == 'sv57':
        superpage_mode_level = 'petapage'
    elif terapage == True and (paging_mode == 'sv48' or paging_mode == 'sv57'):
        superpage_mode_level = 'terapage'
    elif gigapage == True and (paging_mode == 'sv39' or
            paging_mode == 'sv48' or
            paging_mode == 'sv57'):
        superpage_mode_level = 'gigapage'
    elif megapage == True and (paging_mode == 'sv32' or 
            paging_mode == 'sv39' or
            paging_mode == 'sv48' or paging_mode == 'sv57'):
        superpage_mode_level = 'megapage'
    else:
        superpage_mode_level = 'usual'
    
    # values for setting up pages obtained from the paging mode dictionary
    mode_val = paging_val_dict[paging_mode]['satp_mode_val']
    levels = paging_val_dict[paging_mode]['levels']
    entries = paging_val_dict[paging_mode]['entries']
    shift_amount = paging_val_dict[paging_mode]['shift_amount']
    xlen = paging_val_dict[paging_mode]['xlen']
    paging_offset_constant = paging_val_dict[paging_mode]['paging_offset_constant']
    
    # while generating super pages
    try:
        spage_level = paging_val_dict[paging_mode]['superpage_level']\
                   [superpage_mode_level]
    except KeyError:
        # key error occurs only when superpaging is not enabled.
        logger.debug("Not generating super pages")
        # setting spage_level to -1 to make sure a superpage is not generated by mistake
        spage_level = -1
    
    # leaf PTE to be used for a superpage
    leaf_pte_u = ''
    leaf_pte_s = ''

    # creating misaligned superpages based on the input from test plugin
    # TO-DO fix trap handler to work with both user and supervisor misaligned superpages
    # when a misaligned_superpage flag is true, a suitable misaligned superpage is created
    if user_supervisor_superpage == True:
        if misaligned_superpage == True:
            logger.debug("""Currently, when user and supervisor superpages are 
present, Only the S page is set to be misaligned.
Support for both misaligned user and supervisor pages is not present, yet!""")
            logger.debug('creating misaligned page')
            leaf_pte_u = '\tli t5, 0x200000ff\n'
            leaf_pte_s = '\tli t4, 0x20eeeeef\n'
        else:
            logger.debug("creating both user and supervisor superpages")
            leaf_pte_u = '\tli t5, 0x200000ff\n'
            leaf_pte_s = '\tli t4, 0x200000ef\n'
    elif user_superpage == True:
        logger.debug("creating user superpages only")
        if misaligned_superpage == True:
            logger.debug('creating misaligned page')
            leaf_pte_u = '\tli t5, 0x20eeeeff\n'
        else:
            leaf_pte_u = '\tli t5, 0x200000ff\n'
    else:
        logger.debug("creating supervisor superpages only")
        if misaligned_superpage == True:
            logger.debug('creating misaligned page')
            leaf_pte_s = '\tli t4, 0x20eeeeef\n'
        else:
            leaf_pte_s = '\tli t4, 0x200000ef\n'

    # for creating pages using assembly in the data section
    if xlen == 64:
        word_fill = '.dword'
    else:
        word_fill = '.word'

    # pages should be aligned to a specific boundary based on the paging mode
    # hence the .align directive is used a lot in the data section
    pre = f"\n.align {align}\n\n"

    # setting up the root level pages.
    # this loop would setup all pages except the last level page.
    initial_level_pages_s = ''
    for level in range(levels - 1):
        initial_level_pages_s += (f"l{level}_pt:\n.rept {entries}\n{word_fill} 0x0"
                                  f"\n.endr\n")

    initial_level_pages_u = ''
    if mode == 'user':
        for level in range(1, levels - 1):
            initial_level_pages_u += (f"l{level}_u_pt:\n.rept {entries}\n"
                                      f"{word_fill} 0x0\n.endr\n")

    # assumption that the l3 pt entry 0 will point to 0x80000000
    # 0x80000000 is the starting point for the code memory of chromite.
    # this should be changed when a different DUT with a different memory mapping is
    # to be tested.
    base_address = 0x80000000
    
    # creating variables for filling the PTE entry.
    # all bits except U are assumed to be set at the start of the program.
    # the test is expected to further update the PTEs if required.
    # tHe U bit is set by default in the case of User pages, else it is zero.
    valid_bit = 0x01
    read_bit = 0x02
    write_bit = 0x04
    execute_bit = 0x08
    u_bit_s = 0x00
    u_bit_u = 0x10
    global_bit = 0x20
    access_bit = 0x40
    dirty_bit = 0x80

    # the last level PTE entry in supervisor and user page
    ll_entries_s = ''
    ll_entries_u = ''

    # the base address is always 0x80000000 irrespective of the privilege mode.
    # copying base_address to perform operations on it during setting up 
    # last level user/supervisor page

    base_address_new = base_address
    
    # setting up LL user page
    # mode is obtained from the test plugin.
    if mode == 'user':
        # number of last level entries required is specified by the plugin.
        # by default, it is 64
        for i in range(valid_ll_pages):
            # the following comments assume that the page size is 4KiB (2^12)
            # shifting the base address by 12 since it is necessary that the 
            # address in the PTE should be aligned to 4KiB
            pte_address_u = base_address_new >> power
            # left shifting the address by 10 to accomodate the PTE control/configuration bits
            pte_address_u = pte_address_u << 10
            # the PTE control/configuration bits are set up by ORing the values
            pte_entry_u = pte_address_u | dirty_bit | access_bit | \
                          global_bit | u_bit_u | execute_bit | write_bit | \
                          read_bit | valid_bit
            # the ll_entries_u string is populated with .dword directives (sv39 and above)
            # to setup the last level page in the data section.
            ll_entries_u += '{0} {1} # entry_{2}\n'.format(word_fill,
                hex(pte_entry_u), i)
            # base address is incremented by the page size.
            base_address_new += page_size
    
    # reupdate base_address_new with 0x80000000
    base_address_new = base_address
    # this section is similiar to user ll page setup
    for i in range(valid_ll_pages):
        pte_address_s = base_address_new >> power
        pte_address_s = pte_address_s << 10
        pte_entry_s = pte_address_s | dirty_bit | access_bit | \
                      global_bit | u_bit_s | execute_bit | write_bit | \
                      read_bit | valid_bit
        ll_entries_s += '{0} {1} # entry_{2}\n'.format(word_fill,hex(pte_entry_s), i)
        base_address_new += page_size
    
    # the last level page is populated using assembly using the section of code that follows
    if mode == 'user':
        ll_page_u = (f'l{levels - 1}_u_pt:\n'
                     f'{ll_entries_u}.rept {entries - valid_ll_pages}\n'
                     f'{word_fill} 0x0\n.endr\n')
    else:
        ll_page_u = ''

    ll_page_s = (f'l{levels - 1}_pt:\n'
                 f'{ll_entries_s}.rept {entries - valid_ll_pages}\n'
                 f'{word_fill} 0x0\n.endr\n')

    # this string will be used by UATG to populate the data section of the core.
    out_data_string = pre + initial_level_pages_s + ll_page_s + \
                      initial_level_pages_u + ll_page_u

    # The section following updates the code section of the assembly test.
    # the linking of pages from root level to last level is taken care by the code
    # in the following section.
    out_code_string = []

    # calculation to set up root level pages
    pte_updation = """\n.option norvc
\t# setting up root PTEs
\tla t0, l0_pt # load address of root page\n"""

    # the misaligned superpage tests require the address of the faulting page to be stored
    data_for_misaligned_test = """\n\tla t4, faulty_page_address
\tSREG t0, (t4)
\tla t4, misaligned_superpage
\taddi t5, x0, 1
\tSREG t5, (t4)\n"""

    # the section of code that followis is used to set up the PTEs in the root level pages 
    # and make them point to the right next level PTE
    # loop required to repeat the same based on the levels of pages present.
    for i in range(levels - 1):
        
        # paging_offset_constant is the amount of bytes to be added from the zeroth
        # PTE entry at the zeroth level. Using this, the right PTE is updated with the 
        # address of the next level PTE.
        offset = (f'\tmv t2, t0\n\tli t1, {paging_offset_constant}'
                  '\n\tadd t0, t0, t1\n')
        
        # moving t2 to t0
        move_t0 = '\tmv t0, t2\n'

        # offset to be used at the root page table (zero level)
        offset_root = offset if i == 0 else ''
        
        # t0 usually contains the address of the l0 page
        # this address wiyld have been moved to t2 before the offset was added
        # we then move the address back since the updation of the next level is
        # dependent on the value stored at t0 (ideally address of zeroth entry of previous level)
        offset_move_t0 = move_t0 if i == 0 else ''

        # for a superpage to be created, the PTE at pages in levels before the 
        # last level needs to be updated.
        superpage_entry_s = leaf_pte_s if i == (spage_level - 1) else ''

        # extra code to load the faulty address and misaligned page address
        # required when test would have a misaligned superpage
        s_superpage_address_load = data_for_misaligned_test \
                                    if (i == (spage_level-1)) and \
                                       (misaligned_superpage == True) \
                                       and \
                                       (user_superpage == False) \
                                       else ''
        # the code used to setup the page
        # comments are present as a part of the strings
        # t0 will contain the address of the 
        #           1) zeroth entry of previous level page when level > 0
        #           2) address of the zeroth entry of level zero (root) page when level == 0
        pte_updation += (f"\t# setting up l{i} table to point l{i + 1} table\n"
                         f"\taddi t1, x0, 1 # add value 1 to reg\n"
                         f"\tslli t2, t1, {power} # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page\n"
                         "\tadd t3, t2, t0 # add with the existing address to get address of nextlevel page\n"
                         f"\tsrli t4, t3, {power} # divide that address with page size to keep it aligned to the 'page size' boundary\n"
                         "\tslli t4, t4, 10 # left shift for filling the PTE contorl/configuration bits\n"
                         "\tadd t4, t4, t1 # set valid bit to 1\n"
                         f"{offset_root}"
                         f"{superpage_entry_s}"
                         "\tSREG t4, (t0) # update the PTE entry \n"
                         f"{s_superpage_address_load}\n"
                         f"{offset_move_t0} # store l{i + 1} first entry address into the first entry of l{i}\n\n")

        # copy the address of the zeroth entry of the current level page
        # used by the level+1 page setup to calculate address
        if i < levels-2:
            pte_updation += ("\t#address updation\n"
                             "\tadd t0, t3, 0 # move the address of "
                             f"level {i + 1} page to t0\n\n")
    
    # a new line to split between superviosr page set up and user page set up
    pte_updation += "\n"

    # setting up the user root pages. Similiar to the setting up of supervisor page
    if mode == 'user':
        
        # loading the root level page again. This is because the root (level 0) page is common for user and supervisor pages
        pte_updation += ("""\t# user page table set up
\tla t0, l0_pt # load address of root page\n
\tla t3, l1_u_pt # load address of l1 user page\n\n""")
        

        common_setup = (f"\tsrli t5, t3, {power} # divide that address with page size to keep it aligned to the 'page size' boundary\n"
                        "\tslli t5, t5, 10 # left shift for filling the PTE contorl/configuration bits\n"
                        "\tli t4, 1 # load and then set valid bit to 1\n"
                        "\tadd t5, t5, t4\n")
        common_setup_store = "\tSREG t5, (t0)\n"

        for i in range(levels-1):
            superpage_entry_u = leaf_pte_u if i == (spage_level - 1) else ''
            u_superpage_address_load = data_for_misaligned_test \
                                        if (i == (spage_level-1)) and \
                                           (misaligned_superpage == True) and \
                                           (user_superpage == True)\
                                        else ''

            pte_updation += f"\n\t# update l{levels-3+i} page entry with address of l{levels-2+i} page\n"
            if i != 0:
                pte_updation += """\taddi t2, x0, 1 # load t2 with 1
\tslli t2, t2, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
\tadd t3, t0, t2 # add with the existing address to get address of nextlevel page\n"""
            
            pte_updation += f"{common_setup}\n"
            pte_updation += (f'{superpage_entry_u}\n'
                             f'{common_setup_store}\n'
                             f'{u_superpage_address_load}\n')
            #pte_updation += f'{common_setup_store}'

            if i < levels-2:
                pte_updation += ("\t# address updation\n"
                                f"\tadd t0, t3, 0 # move address of l{i + 1} page into t0\n")

    # the following section deals with creating faulty pages

    # terapage and pertapage will create a fault since chromite's memory is not as large as it is
    # small fix which can be removed once the dependency on using a0 and a1 register is resolved
    if (terapage == True) or (petapage == True):
        a0_reg = 0
    else:
        a0_reg = 173

    if (mode == 'user') and (terapage == False) and (petapage == False):
        # user_supervisor superpgae is not a part of the test because in this 
        # mode initially there is fault on the supervisor page and then 
        # on the user page.
        if (misaligned_superpage == True) and (user_superpage == False):
            a1_reg = 0
        else:
            a1_reg = 173
        # faulting pt_label 
        pt_label = f'l{levels - 1}_u_pt'
    else:
        a1_reg = 0
        pt_label = f'l{levels - 1}_pt'
    # will be fixed when the a0 register dependency is fixed
    # To - DO
    if mode == 'user' and user_superpage == False and misaligned_superpage == True:
        handle_in_supervisor = """\n\t# code to handle pagefault in supervisor mode (will be fixed)
\tla t3, handle_pf_in_supervisor
\taddi t4, x0, 1
\tSREG t4, (t3)\n\n"""
    else:
        handle_in_supervisor = ''
        
    # the faulting bits will be set here
    # UATG allows all types of faults to be generated
    fault_valid_bit = 0x01 if pte_dict['valid'] else 0x00
    fault_read_bit = 0x02 if pte_dict['read'] else 0x00
    fault_write_bit = 0x04 if pte_dict['write'] else 0x00
    fault_execute_bit = 0x08 if pte_dict['execute'] else 0x00
    fault_u_bit = 0x10 if pte_dict['user'] else 0x00
    fault_global_bit = 0x20 if pte_dict['globl'] else 0x00
    fault_access_bit = 0x40 if pte_dict['access'] else 0x00
    fault_dirty_bit = 0x80 if pte_dict['dirty'] else 0x00

    # a special case where the PTE bits are set rather than unset
    # hence, we need to perform an OR with the faulty_pte_val rather tham
    # the usual AND.
    # supervisor accessing user marked pages
    if pte_dict['user'] == True and mode != 'user':
        fault_set = """\t#set u bit in the PTE
\t#special case when U bit is to be set and not unset like usual
\tli t2, 0xff
\tor t3, t3, t2\n"""

    else:
        fault_set = ''
    
    # faulty PTE bits
    faulty_pte_bits = fault_valid_bit | fault_read_bit | fault_write_bit | \
                      fault_execute_bit | fault_u_bit | fault_global_bit | \
                      fault_access_bit | fault_dirty_bit
    
    # the existing LL PTE is updated with the faulty_pte_val
    # we create a mask for updating the LL PTE with the intended (faulty) value
    faulty_pte_val = 0xffffffffffffff00 | faulty_pte_bits

    # labels differ between memory fault test and instruction fault
    # for a memory fault, the faulty PTE/Page is the address from/to where the faulting instruction tried to read/write.
    # for an instruction fault, the faulty PTE/Page is the page in which the faulting instruction is present.
    fault_page_label = "faulting_address" if mem_fault else "faulting_instruction"

    # code to create a fault and also update memory locations with the faulting addresses 
    if fault:
        # the code loads a0 and a1 registers are required
        # then the address of the faulting instruction to the label return address 
        # in the data memory
        # Te trap handler will use this data to return once the fault is handled
        fault_creation = ("\naddress_loading:\n"
                         f"\tli a0, {a0_reg}\n"
                         f"\tli a1, {a1_reg}\n"
                         "\tla t5, faulting_instruction #the address of the faulting instruction is loaded\n"
                         "\tla t6, return_address # return address is a label in the data section\n"
                         "\tSREG t5, 0(t6) # the memory location marked by return_address label is stored with the faulting instruction\n\n"
                         f"{handle_in_supervisor}\n")
        
        # This section updates the correctly setup PTE with a faulty value to raise a PAGE fault
        if (misaligned_superpage == False):
            fault_creation += ("offset_adjustment:\n"
                              "\tli t3, 0x1ff # mask for fault creation\n"
                              "\tli t4, 0x1ff000 # mask for making the low 3 bytes zero\n"
                              f"\tla t5, {fault_page_label} # loading address of PTE which needs to be changed for a fault to happen\n"
                              "\tand t5, t5, t4 # making the low 3 bytes zero\n"
                              "\tsrli t5, t5, 12 # shifting right for obtaining an aligned address\n"
                              "\tand t5, t5, t3 # masking to obtain the offset from zeroth entry of current page level\n"
                              "\tslli t5, t5, 3 # converting offset to bytes\n"
                              f"\tla t6, {pt_label} # loading address of the page table level which will have the faulting pte\n"
                              "\tadd t6, t6, t5 # add offset\n"
                              "\tld t3, 0(t6) # loading the current PTE entry\n"
                              f"\tli t2, {hex(faulty_pte_val)} #storing the faulty PTE value into a register\n"
                              "\tand t3, t3, t2# ANDing with the old value to create a fault\n"
                              f"{fault_set}"
                              "\tSREG t3, 0(t6) # store the faulty PTE back again\n"
                              "\tla t5, faulty_page_address\n"
                              "\tSREG t6, 0(t5) # update the faulty_page_address label with the faulting page's address\n")


    else:
        fault_creation = ""

    pte_updation += fault_creation
    
    # updating a1 reg after entering supervisor mode
    if mode == 'user' and user_superpage == False:
        u_mode_a1_reg = '\n\tli a1, 173\n'
    else:
        u_mode_a1_reg = ''
    
    # creating a string of the macros which are used to move into USER and SUPERVISOR mode
    user_entry = "RVTEST_USER_ENTRY()\n" if mode == 'user' else ""
    user_exit = "RVTEST_USER_EXIT()\n" if mode == 'user' else ""
    
    # mxr bit updation for a specific test case
    mxr_bit_update = ("""\n\t#sum bit updation
\taddi x1, x0, 1
\tslli x2, x1, 19
\tcsrs CSR_MSTATUS, x2\n\n""") if mstatus_mxr_bit == True else ""
    
    # sum bit updation for a specific test case
    sum_bit_update = ("""\n\t#sum bit updation
\taddi x1, x0, 1
\tslli x2, x1, 18
\tcsrs CSR_MSTATUS, x2\n\n""") if mstatus_sum_bit == True else ""

    # appending all the stings to out_code_string
    # the returened string currently has 5 elements which will get added to the 
    # assembly test at the right places
    # the assembly updation is taken care of by the test generator

    out_code_string.append(pte_updation)

    out_code_string.append(sum_bit_update)

    out_code_string.append(mxr_bit_update)

    # macro to enter into SUPERVISOR and then if needed, USER mode from Machine mode
    out_code_string.append(f"\nRVTEST_SUPERVISOR_ENTRY({power}, {mode_val}, {shift_amount})\n"
                           "101:\t# supervisor entry point\n"
                           f"{u_mode_a1_reg}"
                           f"\n{user_entry}"
                           "102:\t# user entry point\n"
                           f".option rvc\n\n")

    # macro to return back from USER mode or supervisor mode to the Machine mode
    out_code_string.append(f"\n\n.option norvc\n{user_exit}"
                           "test_exit:\n"
                           "\nRVTEST_SUPERVISOR_EXIT()\n#assuming va!=pa\n"
                           "supervisor_exit_label:\n")

    return out_code_string, out_data_string


def run_make(work_dir, jobs):
    """
        function to invoke the empty compilation makefile

        :param work_dir: path to the work directory
        :param jobs: number of parallel processes for the make utility to spawn
        :returns: placeholder int
        :rtype: int
    """
    cwd = getcwd()
    chdir(abspath(work_dir))
    logger.debug(f'Current directory is: {work_dir}')
    logger.info(f'Invoking makefile to perform an empty compilation')
    logger.warning(f'Based on the number of tests and their size, '
                   f'this step might take a lot of time.')

    try:
        out = run(split(f'make -j{jobs}'), check=True, stdout=PIPE, stderr=PIPE)
        logger.debug(out.stdout.decode('ascii'))
        logger.info('All the generated Assmebly files are syntatically correct')
        logger.info('Empty Syntax Check - Complete! No errors found.')

    except CalledProcessError as e:
        logger.error(e.stderr.decode('ascii'))
        logger.warning(f'Please fix the errors and re-generate the tests')
        logger.info('Empty Syntax Check - Complete! Error found.')

    chdir(cwd)
    logger.debug(f'Current directory is: {getcwd()}')
    return 1


def paging_modes(yaml_string, isa):
    """
        This function reads the YAML entry specifying the valid 
        paging modses supported by the SATP CSR and returns the mode(s)
        for the framework to generate tests
    """
    split_string = yaml_string.split(' ')
    values = (split_string[-1][1:-1]).split(',')
    valid_list = [int(i) for i in values]

    valid_modes = []

    if 'RV64' in isa:
        if 8 in valid_list:
            valid_modes.append('sv39')
        if 9 in valid_list:
            valid_modes.append('sv48')
        if 10 in valid_list:
            valid_modes.append('sv57')
    else:
        if 1 in valid_list:
            valid_modes.append('sv32')

    return valid_modes


def select_paging_modes(paging_modes):
    """
    Function to read the paging modes specified by the user, 
    and generate only those modes and not every possible paging mode.
    Returns a list of the user selected modes
    """
    mode = []

    if isinstance(paging_modes, tuple):
        mode = list(paging_modes)
        mode.sort()
    elif paging_modes is not None:
        try:
            modes = paging_modes.replace(' ', ',')
            modes = modes.replace(', ', ',')
            modes = modes.replace(' ,', ',')
            mode = list(set(modes.split(",")))
            mode.remove('')
            mode.sort()

        except ValueError:
            pass

    if not mode:
        mode.append('sv39')

    return mode


def macros_parser(_path=[join(dirname(__file__), 'env/arch_test_unpriv.h'),
                         join(dirname(__file__), 'env/arch_test_priv.h')]):
    
    macros = []

    for arch_test_path in _path:

        with open(arch_test_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if '#ifdef' in line:
                pref = line[0:line.find('#ifdef')]
                if '//' not in pref and '/*' not in pref:
                    macros.append(line[line.find('#ifdef') + 6:].strip('\n '))
    
    return list(set(macros))
