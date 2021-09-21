# See LICENSE.incore for license details
"""Console script for uatg."""

import click
from configparser import ConfigParser
from uatg.log import logger
from uatg.test_generator import generate_tests, clean_dirs, validate_tests, \
    generate_sv
from uatg.__init__ import __version__
from uatg.utils import list_of_modules, info, load_yaml, clean_modules
from uatg.utils import create_dut_config_files, create_config_file, \
    create_alias_file


@click.group()
@click.version_option(version=__version__)
def cli():
    """RISC-V \u00b5-Architectural Test Generator (UATG)"""


# -----------------


@click.version_option(version=__version__)
@click.option('--module_dir',
              '-md',
              multiple=False,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Absolute Path to the directory containing the python files"
                   " which generates the assembly tests. "
                   "Required Parameter")
@click.option('--work_dir',
              '-wd',
              multiple=False,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the working directory where generated files will be"
                   " stored.")
@click.option('--verbose',
              '-v',
              default='info',
              help='Set verbose level for debugging',
              type=click.Choice(['info', 'error', 'debug'],
                                case_sensitive=False))
@cli.command()
def clean(module_dir, work_dir, verbose):
    """
    Removes ASM, SV and other generated files from the work directory, and
    removes .yapsy plugins from module directory.\n
    Requires: -wd, --work_dir\n
    Optional: -md, --module_dir; -v, --verbose
    """
    logger.level(verbose)
    info(__version__)
    logger.debug('Invoking clean_dirs')
    clean_dirs(work_dir=work_dir, modules_dir=module_dir)


# -------------------------


@click.version_option(version=__version__)
@click.option('--alias_file',
              '-af',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the aliasing file containing containing BSV alias "
                   "names.")
@click.option('--configuration',
              '-cfg',
              multiple=True,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              # TODO: Update documentation here!
              help="Path to the yaml file containing DUT configuration. "
                   "Needed to generate/validate tests")
@click.option('--module_dir',
              '-md',
              multiple=False,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Absolute Path to the directory containing the python files"
                   " which generates the assembly tests. "
                   "Required Parameter")
@click.option('--gen_cvg',
              '-gc',
              is_flag=True,
              required=False,
              help='Set this flag to generate the Covergroups')
@click.option(
    '--gen_test_list',
    '-t',
    is_flag=True,
    required=False,
    help='Set this flag if a test-list.yaml is to be generated by uatg. '
         'uatg does not generate the test_list by default.')
@click.option('--linker_dir',
              '-ld',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the directory containing the linker file. Work "
                   "Directory is Chosen for linker if this argument is empty")
@click.option('--work_dir',
              '-wd',
              multiple=False,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the working directory where generated files will be"
                   " stored.")
@click.option('--modules',
              '-m',
              default='all',
              multiple=False,
              is_flag=False,
              help="Enter a list of modules as a string in a comma separated "
                   "format.\ndefault-all",
              type=str)
@click.option('--verbose',
              '-v',
              default='info',
              help='Set verbose level for debugging',
              type=click.Choice(['info', 'error', 'debug'],
                                case_sensitive=False))
@cli.command()
def generate(alias_file, configuration, linker_dir, module_dir, gen_cvg,
             gen_test_list, work_dir, modules, verbose):
    """
    #TODO change documentation here!
    Generates tests, cover-groups for a list of modules corresponding to the DUT
    defined in dut_config inside the work_dir. Can also generate the test_list
    needed to execute them on RiverCore.\n
    Requires: -cfg, --configuration, -md, --module_dir; -wd, --work_dir\n
    Depends : (-gc, --gen_cvg -> -af, --alias_file)\n
    Optional: -gc, --gen_cvg; -t, --gen_test_list; -ld, --linker_dir;\n
              -m, --modules; -v, --verbose
    """
    logger.level(verbose)
    info(__version__)

    dut_dict = {}
    try:
        dut_dict['rv64i_isa'] = load_yaml(configuration[0])  # Yaml for ISA
    except IndexError:
        logger.error('rv64i_isa path is missing. UATG Can not proceed without '
                     'providing a path to rv64i_isa.yaml file')
        raise Exception('MISSING_RV64I_ISA')
    try:
        dut_dict['core64'] = load_yaml(configuration[1])  # Yaml for ISA
    except IndexError:
        logger.error('core64 path is missing. UATG Can not proceed without '
                     'providing a path to rv64i_isa.yaml file')
        raise Exception('MISSING_CORE64')
    try:
        dut_dict['rv64i_custom'] = load_yaml(
            configuration[2])  # Yaml for Modules
    except IndexError:
        logger.error('rv64i_custom path is missing. UATG Can not proceed '
                     'without providing a path to rv64i_custom.yaml file')
        raise Exception('MISSING_RV64I_CUSTOM')
    try:
        dut_dict['csr_grouping'] = load_yaml(configuration[3])
    except IndexError:
        logger.error('csr_grouping.yaml parameter is missing')
        raise Exception('MISSING_RV64I_ISA')

    module = clean_modules(module_dir, modules)

    generate_tests(work_dir=work_dir,
                   linker_dir=linker_dir,
                   modules_dir=module_dir,
                   modules=module,
                   config_dict=dut_dict,
                   test_list=str(gen_test_list))
    if gen_cvg:
        if alias_file is not None:
            alias_dict = load_yaml(alias_file)
            generate_sv(work_dir=work_dir,
                        config_dict=dut_dict,
                        modules_dir=module_dir,
                        modules=module,
                        alias_dict=alias_dict)
        else:
            logger.error('Can not generate covergroups without alias_file.')
            exit('GEN_CVG WITHOUT ALIAS_FILE')


# -------------------------


@click.version_option(version=__version__)
@click.option('--verbose',
              '-v',
              default='info',
              help='Set verbose level for debugging',
              type=click.Choice(['info', 'error', 'debug'],
                                case_sensitive=False))
@click.option('--module_dir',
              '-md',
              multiple=False,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Absolute Path to the directory containing the python files"
                   " which generates the assembly tests. "
                   "Required Parameter")
@cli.command()
def list_modules(module_dir, verbose):
    """
    Provides the list of modules supported from the module_dir\n
    Requires: -md, --module_dir
    """
    logger.level(verbose)
    module_str = "\nSupported modules:\n"
    for module in (list_of_modules(module_dir)):
        module_str += '\t' + module + '\n'
    print(f'{module_str}')


# -------------------------


@click.option(
    '--config_file',
    '-c',
    multiple=False,
    required=True,
    type=click.Path(exists=True, resolve_path=True, readable=True),
    help="Provide a config.ini file's path. This runs uatg based upon "
         "the parameters stored in the file. If not specified "
         "individual args/flags are to be passed through cli. In the"
         "case of conflict between cli and config.ini values, config"
         ".ini values will be chosen")
@click.option('--verbose',
              '-v',
              default='info',
              help='Set verbose level for debugging',
              type=click.Choice(['info', 'error', 'debug'],
                                case_sensitive=False))
@cli.command()
def from_config(config_file, verbose):
    """
    This subcommand reads parameters from config.ini and runs uatg based on the
    values.\n
    Optional: -c, --config
    """

    config = ConfigParser()
    config.read(config_file)

    module_dir = config['uatg']['module_dir']
    modules = config['uatg']['modules']
    verbose = config['uatg']['verbose']
    logger.level(verbose)
    module = clean_modules(module_dir, modules)

    info(__version__)
    dut_dict = {}

    if config['uatg']['gen_test'].lower() == 'true' or \
       config['uatg']['gen_cvg'].lower() == 'true' or \
       config['uatg']['val_test'].lower() == 'true':

        configuration = config['uatg']['configuration_files'].split(',')
        try:
            dut_dict['rv64i_isa'] = load_yaml(configuration[0])  # Yaml for ISA
        except IndexError:
            logger.error(
                'rv64i_isa path is missing. UATG Can not proceed without '
                'providing a path to rv64i_isa.yaml file')
            raise Exception('MISSING_RV64I_ISA')
        try:
            dut_dict['core64'] = load_yaml(configuration[1])  # Yaml for ISA
        except IndexError:
            logger.error('core64 path is missing. UATG Can not proceed without '
                         'providing a path to rv64i_isa.yaml file')
            raise Exception('MISSING_CORE64')
        try:
            dut_dict['rv64i_custom'] = load_yaml(
                configuration[2])  # Yaml for Modules
        except IndexError:
            logger.error('rv64i_custom path is missing. UATG Can not proceed '
                         'without providing a path to rv64i_custom.yaml file')
            raise Exception('MISSING_RV64I_CUSTOM')
        try:
            dut_dict['csr_grouping'] = load_yaml(configuration[3])
        except IndexError:
            logger.error('csr_grouping.yaml parameter is missing')
            raise Exception('MISSING_RV64I_ISA')

    if config['uatg']['gen_test'].lower() == 'true':
        generate_tests(work_dir=config['uatg']['work_dir'],
                       linker_dir=config['uatg']['linker_dir'],
                       modules_dir=module_dir,
                       modules=module,
                       config_dict=dut_dict,
                       test_list=config['uatg']['gen_test_list'])

    if config['uatg']['gen_cvg'].lower() == 'true':

        alias_dict = load_yaml(config['uatg']['alias_file'])
        generate_sv(work_dir=config['uatg']['work_dir'],
                    modules=module,
                    modules_dir=module_dir,
                    config_dict=dut_dict,
                    alias_dict=alias_dict)

    if config['uatg']['val_test'].lower() == 'true':

        validate_tests(modules=module,
                       work_dir=config['uatg']['work_dir'],
                       config_dict=dut_dict,
                       modules_dir=module_dir)

    if config['uatg']['clean'].lower() == 'true':
        logger.debug('Invoking clean_dirs')
        clean_dirs(work_dir=config['uatg']['work_dir'], modules_dir=module_dir)


# -------------------------


@click.option('--config_path',
              '-cp',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Directory to store the config.ini file")
@click.option('--alias_path',
              '-ap',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Directory to store the aliasing.yaml file")
@click.option('--dut_path',
              '-dp',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Directory to store the dut_config.yaml file")
@cli.command()
def setup(config_path, alias_path, dut_path):
    """
        Setups template files for config.ini, dut_config.yaml and aliasing.yaml.
        Optionally you can provide the path's for each of them. If not specified
        files will be written to default paths.\n
        Optional: -dp, --dut_path;  -ap, --alias_path; -cp, --config_path
    """

    if config_path is None:
        config_path = './'
    if alias_path is None:
        alias_path = './'
    if dut_path is None:
        dut_path = './'

    create_config_file(config_path=config_path)
    # TODO: modify these functions to write 4 separate yamls
    create_dut_config_files(dut_config_path=dut_path)
    create_alias_file(alias_path=alias_path)

    print(f'Files created')


# -------------------------


@click.version_option(version=__version__)
@click.option('--configuration',
              '-cfg',
              multiple=True,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              # TODO: Update documentation here!
              help="Path to the yaml file containing DUT configuration. "
                   "Needed to generate/validate tests")
@click.option('--module_dir',
              '-md',
              multiple=False,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Absolute Path to the directory containing the python files"
                   " which generate the assembly tests. "
                   "Required Parameter")
@click.option('--work_dir',
              '-wd',
              multiple=False,
              required=True,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the working directory where generated files will be"
                   " stored.")
@click.option('--modules',
              '-m',
              default='all',
              multiple=False,
              is_flag=False,
              help="Enter a list of modules as a string in a comma separated "
                   "format.\ndefault-all",
              type=str)
@click.option('--verbose',
              '-v',
              default='info',
              help='Set verbose level for debugging',
              type=click.Choice(['info', 'error', 'debug'],
                                case_sensitive=False))
@cli.command()
def validate(configuration, module_dir, work_dir, modules, verbose):
    logger.level(verbose)
    info(__version__)
    dut_dict = {}
    try:
        dut_dict['rv64i_isa'] = load_yaml(configuration[0])  # Yaml for ISA
    except IndexError:
        logger.error(
            'rv64i_isa path is missing. UATG Can not proceed without '
            'providing a path to rv64i_isa.yaml file')
        raise Exception('MISSING_RV64I_ISA')
    try:
        dut_dict['core64'] = load_yaml(configuration[1])  # Yaml for ISA
    except IndexError:
        logger.error('core64 path is missing. UATG Can not proceed without '
                     'providing a path to rv64i_isa.yaml file')
        raise Exception('MISSING_CORE64')
    try:
        dut_dict['rv64i_custom'] = load_yaml(
            configuration[2])  # Yaml for Modules
    except IndexError:
        logger.error('rv64i_custom path is missing. UATG Can not proceed '
                     'without providing a path to rv64i_custom.yaml file')
        raise Exception('MISSING_RV64I_CUSTOM')
    try:
        dut_dict['csr_grouping'] = load_yaml(configuration[3])
    except IndexError:
        logger.error('csr_grouping.yaml parameter is missing')
        raise Exception('MISSING_RV64I_ISA')

    module = clean_modules(module_dir, modules)
    validate_tests(modules=module,
                   work_dir=work_dir,
                   config_dict=dut_dict,
                   modules_dir=module_dir)
