import ruamel
from ruamel.yaml import YAML
import os
import glob
from utg.log import logger


# import utg
# from yapsy.PluginManager import PluginManager


def list_of_modules(module_dir, verbose='error'):
    logger.level(verbose)
    if os.path.exists(os.path.join(module_dir, 'index.yaml')):
        modules = load_yaml(os.path.join(module_dir, 'index.yaml'))
        module_str = "Supported modules:\n"
        for key, value in modules.items():
            if value is not None:
                module_str += '\t' + key + '\n'
        return module_str
    else:
        logger.error(f"index.yaml not found in {module_dir}")
        exit("FILE_NOT_FOUND")


def info(version):
    logger.info('****** Micro Architectural Tests *******')
    logger.info('Version : {0}'.format(version))
    logger.info('Copyright (c) 2021, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')


def load_yaml(foo):
    if foo.endswith('.yaml') or foo.endswith('.yml'):
        yaml = YAML(typ="safe")
        yaml.default_flow_style = False
        yaml.allow_unicode = True
        try:
            with open(foo, "r") as file:
                return yaml.load(file)
        except ruamel.yaml.constructor.DuplicateKeyError as msg:
            logger.error(f'error: {msg}')
    else:
        logger.error(f'error: {foo} is not a valid yaml file')
        exit('INVALID_FILE')


# def clean_cli_params(config_file, module, gen_test, val_test, module_dir,
#                      gen_cvg, clean, alias_file, list_modules):
#     error = (False, '')
#     dut_yaml = load_yaml(config_file)
#     if (gen_test or val_test) and config_file is None:
#         error = (True, 'The --config_file/-cf option is missing.\n'
#                        'Exiting utg. Fix the issue and Retry.')
#         return error
#
#     if config_file is not None:
#         try:
#             dut_yaml = load_yaml(config_file)
#         except Exception:
#             error = (True,
#                      f'The specified config file {config_file} does not '
#                      f'exist or is not in the YAML format.\nExiting utg. '
#                      f'Fix the issue and Retry.')
#             return error
#         else:
#             error = (True, 'The specified dut_config file does not have a '
#                            '.yaml extension. Please choose a YAML file')
#             return error
#
#     if alias_file is not None:
#         if alias_file[-5:] == '.yaml' or alias_file[-5:] == '.yml':
#             try:
#                 alias_yaml = load_yaml(alias_file)
#             except Exception as e:
#                 error = (True,
#                          f'The specified alias file {alias_file} does not '
#                          f'exist or is not in the YAML format.\nExiting utg. '
#                          f'Fix the issue and Retry.')
#                 return error
#         else:
#             error = (True,
#                      'The specified alias_config file does not have a .yaml'
#                      ' extension. Please choose a YAML file')
#             return error
#     if gen_cvg and not alias_file:
#         error = (True, 'Cannot generate covergroups without the alias file\n'
#                        'Please provide the alias file with the -af flag'
#                        ' and try again')
#         return error
#
#     if (gen_test or val_test or clean or list_modules) and
#     (module_dir is None):
#         error = (True, 'The --module_dir/-md option is missing.\n'
#                        'Exiting utg. Fix the issue and Retry.')
#         return error
#
#     if (module_dir is not None) and not os.path.isdir(module_dir):
#         error = (True, 'The specified module directory does not exist.\n'
#                        'Exiting utg. Fix the issue and Retry.')
#
#         return error
#
#     if gen_cvg and not gen_test:
#         error = (True,
#                  'Cannot generate covergroups without generating the tests\n'
#                  'If you are trying to validate tests, remove the'
#                  'generate_covergroups as well as generate_tests option'
#                  'and try again')
#         return error
#
#     available_modules = list_of_modules(module_dir)
#
#     try:
#         module = module.replace(' ', ',')
#         module = module.replace(', ', ',')
#         module = module.replace(' ,', ',')
#         module = list(set(module.split(",")))
#         module.remove('')
#         module.sort()
#     except ValueError:
#         pass
#     for i in module:
#         if i not in available_modules:
#             error = (True, f'Module {i} is not supported/unavailable.')
#
#     if 'all' in module:
#         module = ['all']
#
#     return module, error, dut_yaml, alias_yaml


def create_plugins(plugins_path):
    files = os.listdir(plugins_path)
    for i in files:
        if ('.py' in i) and (not i.startswith('.')):
            module_name = i[0:-3]
            f = open(plugins_path + '/' + module_name + '.yapsy-plugin', "w")
            f.write("[Core]\nName=" + module_name + "\nModule=" + module_name)
            f.close()


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
        test_list[base_key]['linker_file'] = target_dir + '/' + 'link.ld'
        test_list[base_key][
            'asm_file'] = os.path.join(asm_dir, base_key, base_key + '.S')
        test_list[base_key]['include'] = [env_dir, target_dir]
        test_list[base_key]['compile_macros'] = ['XLEN=64']
        test_list[base_key]['extra_compile'] = []
        test_list[base_key]['result'] = 'Unavailable'

    return test_list


def create_linker(target_dir):
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


def join_yaml_reports(work_dir='absolute_path_here/',
                      module='branch_predictor'):
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


class sv_components:
    # class with methods to generate system verilog files
    def __init__(self, config_file):
        """
        This class contains the methods which will return the tb_top and
        interface files
        """
        super().__init__()
        self._btb_depth = 32
        # config = ConfigParser()
        config = config_file
        self.rg_initialize = config['bpu']['reg']['bpu_rg_initialize']
        self.rg_allocate = config['bpu']['reg']['bpu_rg_allocate']
        self.btb_tag = config['bpu']['wire']['bpu_btb_tag']
        self.btb_entry = config['bpu']['wire']['bpu_btb_entry']
        self.ras_top_index = config['bpu']['wire']['bpu_ras_top_index']
        self.rg_ghr = config['bpu']['reg']['bpu_rg_ghr']
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
        interface = ("interface chromite_intf(input bit CLK,RST_N);\n"
                     "  logic " + str(self.rg_initialize) + ";\n"
                                                            "  logic [4:0]" +
                     str(self.rg_allocate) + ";\n")
        interface += "\n  logic [7:0]{0};".format(self.rg_ghr)
        interface += "\nlogic [" + str(self._btb_depth - 1) + ":0]{0};".format(
            self.valids)
        interface += "\n  logic {0};".format(self.ras_top_index)
        interface += "\n  logic [8:0]{0};\n".format(self.mispredict)
        for i in range(self._btb_depth):
            interface += "\n  logic [62:0] " + str(self.btb_tag) + "_" + str(
                i) + ";"
        for i in range(self._btb_depth):
            interface += "\n  logic [67:0] " + str(
                self.btb_entry) + "_" + str(i) + ";"
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
        # tb_top = tb_top + "\tif(!RST_N) begin\n\tintf.{0} = {1}.{
        # 0};\n\tintf.{2} = {1}.{2};\n\tintf.{3} = {1}.{3};\n\tintf.{4} = {
        # 1}.{4};\n\tintf.{5} = {1}.{5};".format(self.rg_initialize,
        # self.bpu_path, self.rg_allocate,self.ras_top_index, self.rg_ghr,
        # self.mispredict)
        tb_top += f"\tif(!RST_N) begin\n\tintf.{self.rg_initialize} = " \
                  f"{self.bpu_path}.{self.rg_initialize};\n\tintf." \
                  f"{self.rg_allocate} = {self.bpu_path}.{self.rg_allocate};" \
                  f"\n\tintf.{self.ras_top_index} = {self.bpu_path}." \
                  f"{self.ras_top_index};\n\tintf.{self.rg_ghr} = " \
                  f"{self.bpu_path}.{self.rg_ghr};\n\tintf.{self.mispredict}" \
                  f" = {self.bpu_path}.{self.mispredict}; "
        for i in range(self._btb_depth):
            tb_top = tb_top + "\n\tintf." + str(
                self.btb_tag) + "_" + str(i) + " = " + str(
                self.bpu_path) + "." + str(
                self.btb_tag) + "_" + str(i) + ";"
        for i in range(self._btb_depth):
            tb_top = tb_top + "\n\tintf." + str(
                self.btb_entry) + "_" + str(i) + " = " + str(
                self.bpu_path) + "." + str(
                self.btb_entry) + "_" + str(i) + ";"
        for i in range(self._btb_depth):
            tb_top = tb_top + f"\n\tintf.{self.valids}[{i}] = {self.bpu_path}" \
                              f".{self.btb_tag}_{i}[0];"
        tb_top += "\n\tend\n\telse\n\tbegin\n"
        tb_top += f"\tintf.{self.rg_initialize} = {self.bpu_path}" \
                  f".{self.rg_initialize};\n\tintf.{self.rg_allocate} = " \
                  f"{self.bpu_path}.{self.rg_allocate};\n\tintf." \
                  f"{self.ras_top_index} = {self.bpu_path}" \
                  f".{self.ras_top_index};\n\tintf.{self.rg_ghr} = " \
                  f"{self.bpu_path}.{self.rg_ghr};\n\tintf.{self.mispredict}" \
                  f" = {self.bpu_path}.{self.mispredict}; "
        for i in range(self._btb_depth):
            tb_top = tb_top + "\n\tintf." + str(
                self.btb_tag) + "_" + str(i) + " = " + str(
                self.bpu_path) + "." + str(
                self.btb_tag) + "_" + str(i) + ";"
        for i in range(self._btb_depth):
            tb_top = tb_top + "\n\tintf." + str(
                self.btb_entry) + "_" + str(i) + " = " + str(
                self.bpu_path) + "." + str(
                self.btb_entry) + "_" + str(i) + ";"
        for i in range(self._btb_depth):
            tb_top = tb_top + "\n\tintf." + str(
                self.valids) + "[" + str(i) + "] = " + str(
                self.bpu_path) + "." + str(
                self.btb_tag) + "_" + str(i) + "[0];"
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
        defines = """/// All compile time macros will be defined here

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
`define TEST """ + str(self.test)

        return defines


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
