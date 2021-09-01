import os
import glob
import random as rnd
from utg.log import logger
import ruamel
from ruamel.yaml import YAML

# import utg
# from yapsy.PluginManager import PluginManager


class sv_components:
    """
        This class contains the methods which will return the tb_top and
        interface files
    """

    def __init__(self, config_file):
        super().__init__()
        self._btb_depth = 32
        # config = ConfigParser()
        config = config_file
        self.rg_initialize = config['bpu']['register']['bpu_rg_initialize']
        self.rg_allocate = config['bpu']['register']['bpu_rg_allocate']
        self.btb_tag = config['bpu']['wire']['bpu_btb_tag']
        self.btb_entry = config['bpu']['wire']['bpu_btb_entry']
        self.ras_top_index = config['bpu']['wire']['bpu_ras_top_index']
        self.rg_ghr = config['bpu']['register']['bpu_rg_ghr']
        self.valids = config['bpu']['wire']['bpu_btb_tag_valid']
        self.mispredict = config['bpu']['wire']['bpu_mispredict_flag']
        self.bpu_path = config['tb_top']['path_to_bpu']
        self.decoder_path = config['tb_top']['path_to_decoder']
        self.stage0_path = config['tb_top']['path_to_stage0']
        self.fn_decompress_path = config['tb_top']['path_to_fn_decompress']
        self.test = config['test_case']['test']

    # function to generate interface file
    def generate_interface(self):
        """
           returns interface file
        """
        interface = f"interface chromite_intf(input bit CLK,RST_N);\n\t" \
                    f"logic {self.rg_initialize};\n\tlogic [4:0" \
                    f"]{self.rg_allocate};\n"
        interface += "\n  logic [7:0]{0};".format(self.rg_ghr)
        interface += f"\nlogic [{self._btb_depth - 1}:0]{self.valids};"
        interface += "\n  logic {0};".format(self.ras_top_index)
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
if(test == \"gshare_fa_ghr_zeros_01\" || test == \"gshare_fa_ghr_ones_01\" || test == \"gshare_fa_ghr_alternating_01\")
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

        # function to generate tb_top file

    def generate_tb_top(self):
        """
          returns tb_top file
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
            tb_top = tb_top + f"\n\tintf.{self.btb_tag}_{loop_var} = {self.bpu_path}" \
                              f".self.btb_tag_{loop_var};"
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.btb_entry}_{loop_var} = " \
                              f"{self.bpu_path}.{self.btb_entry}_{loop_var};"
        for loop_var in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.valids}[{loop_var}] = {self.bpu_path}" \
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
            tb_top = tb_top + f"\n\tintf.{self.valids}[{loop_var}] = {self.bpu_path}" \
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

    def generate_defines(self):
        """
        creates the defines.sv file
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
    logger.info('****** Micro Architectural Tests *******')
    logger.info('Version : {0}'.format(version))
    logger.info('Copyright (c) 2021, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')


def load_yaml(file):
    """
        Function to load YAML Files.
    """
    if file.endswith('.yaml') or file.endswith('.yml'):
        yaml = YAML(typ="safe")
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        try:
            with open(file, "r") as file:
                return yaml.load(file)
        except ruamel.yaml.constructor.DuplicateKeyError as msg:
            logger.error(f'error: {msg}')
    else:
        logger.error(f'error: {file} is not a valid yaml file')
        exit('INVALID_FILE')


def join_yaml_reports(work_dir='abs_path_here/', module='branch_predictor'):
    """
        Function that combines all the verification report yaml files into one
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
        Creates a template linker file in the target_dir
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

    with open(target_dir + '/' + "link.ld", "w") as outfile:
        outfile.write(out)


def create_model_test_h(target_dir):
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

    with open(target_dir + '/' + 'model_test.h', 'w') as outfile:
        outfile.write(out)


def create_plugins(plugins_path):
    files = os.listdir(plugins_path)
    for file in files:
        if ('.py' in file) and (not file.startswith('.')):
            module_name = file[0:-3]
            f = open(plugins_path + '/' + module_name + '.yapsy-plugin', "w")
            f.write("[Core]\nName=" + module_name + "\nModule=" + module_name)
            f.close()


def create_config_file(config_path):
    """
        Creates a template config.ini file at the config_path directory.
        Invoked by running utg setup
    """
    cfg = '[utg]\n\n# [info, error, debug] set verbosity level to view ' \
          'different levels of messages.\nverbose = info\n# [True, False] ' \
          'the clean flag removes unnecessary files from the previous runs ' \
          'and cleans directories\nclean = False\n\n# Enter the modules whose' \
          ' tests are to be generated/validated in comma separated format.\n# '\
          'Run \'utg --list-modules\' to find all the modules that are ' \
          'supported.\n# Use \'all\' to generate/validate all modules\n' \
          'modules = all\n\n# Absolute path of the uarch_modules/modules ' \
          'Directory\nmodule_dir = uarch_modules/modules\n# Directory to dump '\
          'assembly files and reports\nwork_dir = work\n# location to store ' \
          'the link.ld linker file. By default it\'s same as ' \
          'work_dir\nlinker_dir = work\n\n# Path of the yaml file containing ' \
          'DUT Configuration.\n# By default the configuration is ' \
          '"utg/target/dut_config.yaml"\ndut_config = ' \
          'target/dut_config.yaml\n# Absolute Path of the yaml file contain' \
          'ing the signal aliases of the DUT\n# presently it is stored ' \
          'in \'uarch_modules/aliasing.yaml\'\nalias_file = ' \
          'uarch_modules/aliasing.yaml\n\n# [True, False] If the gen_test_' \
          'list flag is True, the test_list.yaml needed for running tests in ' \
          'river_core are generated automatically.\n# Until you want to ' \
          'validate individual tests in river_core set the flag to True\n' \
          'gen_test_list = True\n# [True, False] If the gen_test flag is True' \
          ', assembly files are generated/overwritten\ngen_test = False\n# ' \
          '[True, False] If the val_test flag is True, assembly files are ' \
          'executed and the modules are validated\nval_test = False\n# [True' \
          ', False] If the gen_cvg flag is True, System Verilog cover-groups ' \
          'are generated\ngen_cvg = False\n\n# list_modules = False'
    with open(os.path.join(config_path, 'config.ini'), 'w') as f:
        f.write(cfg)


def create_alias_file(alias_path):
    """
        Creates a template aliasing.yaml file at the alias_path directory.
        Invoked by running utg setup
    """
    alias = 'tb_top:\n\tpath_to_bpu: ' \
            'mktbsoc.soc.ccore.riscv.stage0.bpu\n\tpath_to_decoder: ' \
            'mktbsoc.soc.ccore.riscv.stage2.instance_decoder_func_32_2\n' \
            '\tpath_to_stage0: mktbsoc.soc.ccore.riscv.stage0\n\t' \
            'path_to_fn_decompress: ' \
            'mktbsoc.soc.ccore.riscv.stage1.instance_fn_decompress_0\n\ntest_' \
            'case:\n\ttest: regression\n\nbpu:\n\tinput:\n\toutput:\n\treg:' \
            '\n\t\tbpu_rg_ghr: rg_ghr_port1__read\n\t\tbpu_rg_initialize: ' \
            'rg_initialize\n\t\tbpu_rg_allocate: ' \
            'rg_allocate\n\twire:\n\t\tbpu_mispredict_flag: ' \
            'ma_mispredict_g\n\t\tbpu_btb_tag: ' \
            'v_reg_btb_tag\n\t\tbpu_btb_entry: ' \
            'v_reg_btb_entry\n\t\tbpu_ras_top_index: ' \
            'ras_stack_top_index_port2__read\n\t\tbpu_btb_tag_valid: ' \
            'btb_valids\n '

    with open(os.path.join(alias_path, 'aliasing.yaml'), 'w') as f:
        f.write(alias)


def create_dut_config(dut_config_path):
    dut = 'ISA: RV64IMAFDCSU\niepoch_size: 2\ndepoch_size: 1\ndtvec_base: ' \
          '256\ns_extension:\n\tmode: sv39\n\titlb_size: 4\n\tdtlb_size: ' \
          '4\n\tasid_width: 9\npmp:\n\tenable: true\n\tentries: ' \
          '4\n\tgranularity: 8\nm_extension:\n\tmul_stages: 1\n\tdiv_stages: ' \
          '32\nbranch_predictor:\n\tinstantiate: True\n\tpredictor: ' \
          'gshare\n\ton_reset: enable\n\tbtb_depth: 32\n\tbht_depth: ' \
          '512\n\thistory_len: 8\n\thistory_bits: 5\n\tras_depth: ' \
          '8\nicache_configuration:\n\tinstantiate: true\n\ton_reset: ' \
          'enable\n\tsets: 64\n\tword_size: 4\n\tblock_size: 16\n\tways: ' \
          '4\n\tfb_size: 4\n\treplacement: RR\n\tecc_enable: false\n\t' \
          'one_hot_select: false\ndcache_configuration:\n\t' \
          'instantiate: true\n\ton_reset: enable\n\tsets: 64\n\tword_size: 8' \
          '\n\tblock_size: 8\n\tways: 4\n\tfb_size: 8\n\tsb_size: 2\n\t' \
          'replacement: RR\n\tecc_enable: false\n\tone_hot_select: false\n\t' \
          'rwports: 1\nreset_pc: 4096\nphysical_addr_size: 32\nbus_protocol: ' \
          'AXI4\nfpu_trap: false\ndebugger_support: false\nno_of_triggers: 0 ' \
          '\ncsr_configuration:\n\tstructure: daisy\n\tcounters_in_grp4: 7\n' \
          '\tcounters_in_grp5: 7\n\tcounters_in_grp6: 7\n\tcounters_in_grp7: ' \
          '8\nbsc_compile_options:\n\ttest_memory_size: 33554432\n\t' \
          'assertions: true\n\ttrace_dump: true\n\tcompile_target: \'sim\'\n' \
          '\tsuppress_warnings: ["all"]\n\tverilog_dir: build/hw/verilog\n\t' \
          'build_dir: build/hw/intermediate\n\ttop_module: mkTbSoc\n\t' \
          'top_file: TbSoc.bsv\n\ttop_dir: test_soc\n\topen_ocd: ' \
          'False\nverilator_configuration:\n\tcoverage: none\n\ttrace: ' \
          'false\n\tthreads: 1\n\tverbosity: true\n\tsim_speed: ' \
          'fast\n\tout_dir: bin'
    with open(os.path.join(dut_config_path, 'dut_config.yaml'), 'w') as f:
        f.write(dut)


def data_section(bit_width=32, random=True, signed=False, align=4):
    data = f'RVTEST_DATA_BEGIN\n.align {align}\n'
    if signed:
        max_val = 2**(bit_width - 1) - 1
        min_val = -2**(bit_width - 1)
    else:
        max_val = 2**bit_width - 1
        min_val = 0
    data += f'MAX_VAL32: .word {max_val}\nMIN_VAL32: .word {min_val}\n'
    if bit_width > 32:
        data += f'MAX_VAL64: .dword {max_val}\nMIN_VAL64: .dword {min_val}\n'
    return data


# UTG Functions
def clean_modules(module_dir, modules, verbose):
    module = None
    available_modules = list_of_modules(module_dir, verbose)

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
      updates the test_list.yaml file of rivercore with the location of the
      tests generated by test_generator as well the directory to dump the logs
    """
    asm_test_list = glob.glob(asm_dir + '/**/*.S')
    env_dir = os.path.join(uarch_dir, 'env/')
    target_dir = asm_dir + '/../'

    for test in asm_test_list:
        logger.debug("Current test is {0}".format(test))
        base_key = os.path.basename(test)[:-2]
        test_list[base_key] = {}
        test_list[base_key]['generator'] = 'utg'
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
    invokes the methods within the sv_components class and creates the sv files
    """
    sv_obj = sv_components(alias_file)
    tb_top = sv_obj.generate_tb_top()
    interface = sv_obj.generate_interface()
    defines = sv_obj.generate_defines()

    with open(sv_dir + "/tb_top.sv", "w") as tb_top_file:
        tb_top_file.write(tb_top)

    with open(sv_dir + "/interface.sv", "w") as interface_file:
        interface_file.write(interface)

    with open(sv_dir + "/defines.sv", "w") as defines_file:
        defines_file.write(defines)


def list_of_modules(module_dir, verbose='error'):
    logger.level(verbose)
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
