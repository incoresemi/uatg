# See LICENSE.incore for license details
"""Console script for uatg."""

import click
from configparser import ConfigParser
from uatg.log import logger
from uatg.test_generator import generate_tests, clean_dirs, validate_tests
from uatg.test_generator import generate_sv
from uatg.__init__ import __version__
from uatg.utils import list_of_modules, info, clean_modules, load_yaml
from uatg.utils import create_dut_config_files, create_config_file
from uatg.utils import combine_config_yamls, create_alias_file, run_make
from logging import getLogger, ERROR
from time import perf_counter

@click.group()
@click.version_option(version=__version__)
def cli():
    """RISC-V Micro-Architectural Test Generator (UATG)"""


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
@click.option(
    '--configuration',
    '-cfg',
    multiple=True,
    required=True,
    type=click.Path(exists=True, resolve_path=True, readable=True),
    help=("Path to the DUT configuration YAML Files. "
          "The YAML files should be specified (space separated) in the "
          "following  order "
          "1. isa_config.yaml "
          "2. core_config.yaml "
          "3. custom_config.yaml "
          "4. csr_grouping.yaml "
          "5. rv_debug.yaml"
          "The ordering should be strictly followed and any deviation will "
          "result in UATG erroring out. This Parameter is needed to "
          "generate/validate tests and also generate "
          "covergroups"))
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
    default=True,
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
@click.option('--index_file',
              '-i',
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to index.yaml file from the tests directory")
@click.option('--jobs',
              '-j',
              default=1,
              help='Number of Jobs for UATG to spawn',
              type=click.INT)
@cli.command()
def generate(alias_file, configuration, linker_dir, module_dir, gen_cvg,
             gen_test_list, work_dir, modules, verbose, index_file, jobs):
    """
    Generates tests, cover-groups for a list of modules corresponding to the DUT
    parameters specified in the configuration yamls, inside the work_dir.
    Can also generate the test_list
    needed to execute them on RiverCore.\n
    Requires: -cfg, --configuration, -md, --module_dir; -wd, --work_dir\n
    Depends : (-gc, --gen_cvg -> -af, --alias_file)\n
    Optional: -gc, --gen_cvg; -t, --gen_test_list; -ld, --linker_dir;\n
              -m, --modules; -v, --verbose
    """
    logger.level(verbose)
    info(__version__)

    dut_dict = combine_config_yamls(configuration)

    module = clean_modules(module_dir, modules)

    generate_tests(work_dir=work_dir,
                   linker_dir=linker_dir,
                   modules_dir=module_dir,
                   modules=module,
                   config_dict=dut_dict,
                   test_list=str(gen_test_list),
                   index_path=index_file,
                   jobs=jobs)
    if gen_cvg:
        if alias_file is not None:
            alias_dict = load_yaml(alias_file)
            generate_sv(work_dir=work_dir,
                        config_dict=dut_dict,
                        modules_dir=module_dir,
                        modules=module,
                        alias_dict=alias_dict,
                        jobs=jobs)
        else:
            logger.error('Can not generate covergroups without alias_file.')
            exit('GEN_CVG WITHOUT ALIAS_FILE')

    logger.info(f'Exiting UATG')
    logger.info(f'Good day! Stay Hydrated.')


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
    Lists the micro-architecture modules of core supported
    among the modules actually present in the DUT\n
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
    help="Provide a config.ini file\'s path. This runs uatg based upon "
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
    Reads config.ini and invokes uatg with read paramaters.\n
    Optional: -c, --config
    """
    start_time = perf_counter()

    config = ConfigParser()
    config.read(config_file)

    module_dir = config['uatg']['module_dir']
    modules = config['uatg']['modules']
    config_work_dir = config['uatg']['work_dir']
    config_linker_dir = config['uatg']['linker_dir']
    config_test_list_flag = config['uatg']['gen_test_list']
    excluded_modules = config['uatg']['excluded_modules']
    index_yaml_path = config['uatg']['index_file']
    # Uncomment to overwrite verbosity from config file.
    # verbose = config['uatg']['verbose']

    logger.level(verbose)
    getLogger('yapsy').setLevel(ERROR)

    info(__version__)

    module = clean_modules(module_dir, modules, excluded_modules)

    try:
        jobs = int(config['uatg']['jobs'])
    except ValueError:
        jobs = 1

    dut_dict = None
    if config['uatg']['gen_test'].lower() == 'true' or \
            config['uatg']['gen_cvg'].lower() == 'true' or \
            config['uatg']['val_test'].lower() == 'true':
        configuration = config['uatg.configuration_files']
        dut_dict = combine_config_yamls(configuration)

    if config['uatg']['gen_test'].lower() == 'true':
        generate_tests(work_dir=config_work_dir,
                       linker_dir=config_linker_dir,
                       modules_dir=module_dir,
                       modules=module,
                       config_dict=dut_dict,
                       test_list=config_test_list_flag,
                       index_path=index_yaml_path,
                       jobs=jobs)

    if config['uatg']['test_compile'].lower() == 'true':
        logger.info(f'Empty Compilation is enabled')
        logger.info(f'UATG will use RISCV-GCC to check if the generated '
                    f'assembly tests are syntatically correct')
        run_make(work_dir=config_work_dir, jobs=jobs)

    if config['uatg']['gen_cvg'].lower() == 'true':
        alias_dict = load_yaml(config['uatg']['alias_file'])
        generate_sv(work_dir=config_work_dir,
                    modules=module,
                    modules_dir=module_dir,
                    config_dict=dut_dict,
                    alias_dict=alias_dict,
                    jobs=jobs)

    if config['uatg']['val_test'].lower() == 'true':
        validate_tests(modules=module,
                       work_dir=config_work_dir,
                       config_dict=dut_dict,
                       modules_dir=module_dir)

    if config['uatg']['clean'].lower() == 'true':
        logger.debug('Invoking clean_dirs')
        clean_dirs(work_dir=config_work_dir, modules_dir=module_dir)
    end_time = perf_counter()

    logger.debug(f'Execution time is {end_time - start_time}s')
    logger.info(f'Exiting UATG')
    logger.info(f'Good day! Stay Hydrated.')

# -------------------------


@click.option('--config_path',
              '-cp',
              multiple=False,
              required=False,
              default='./',
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Directory to store the config.ini file")
@click.option('--jobs',
              '-j',
              multiple=False,
              required=False,
              default=1,
              type=click.INT,
              help="No. of jobs to be spawned by uatg")
@click.option('--modules',
              '-m',
              multiple=False,
              required=False,
              default='all',
              type=click.STRING,
              help="Modules to generate code for...")
@click.option('--module_dir',
              '-md',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the modules directory")
@click.option('--work_dir',
              '-wd',
              multiple=False,
              required=False,
              default='./',
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the working directory where generated files will be"
              " stored.")
@click.option('--linker_dir',
              '-ld',
              multiple=False,
              required=False,
              default='./',
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the linker directory")
@click.option('--test_compile',
              '-tc',
              is_flag=True,
              required=False,
              default=False,
              help='Set this flag to generate the Covergroups')
@click.option(
    '--configuration',
    '-cfg',
    multiple=True,
    required=True,
    type=click.Path(exists=True, resolve_path=True, readable=True),
    help=("Path to the DUT configuration YAML Files. "
          "The YAML files should be specified (space separated) in the "
          "following  order "
          "1. isa_config.yaml "
          "2. core_config.yaml "
          "3. custom_config.yaml "
          "4. csr_grouping.yaml "
          "5. rv_debug.yaml"
          "The ordering should be strictly followed and any deviation will "
          "result in  UATG erroring out. This Parameter is needed to "
          "generate/validate tests and also generate covergroups"))
@click.option('--alias_path',
              '-ap',
              multiple=False,
              required=False,
              default='./',
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Directory to store the aliasing.yaml file")
@click.option('--dut_path',
              '-dp',
              multiple=False,
              required=False,
              default='./',
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Directory to store the DUT configuration yaml files")

@cli.command()
def setup(config_path, jobs, modules, module_dir, work_dir, linker_dir,
          configuration, alias_path, test_compile, dut_path):
    """
        Creates template configuration files.

        Setups template files for config.ini, dut_config.yaml and aliasing.yaml.
        Optionally you can provide the path\'s for each of them. If not
        specified files will be written to default paths.\n
        Optional: -dp, --dut_path;  -ap, --alias_path; -cp, --config_path
    """

    create_config_file(config_path=config_path, jobs=jobs,
                       modules=modules, module_dir=module_dir,
                       work_dir=work_dir, linker_dir=linker_dir,
                       alias_path=alias_path, test_compile=test_compile,
                       cfg_files=configuration
                       )
    create_dut_config_files(dut_config_path=dut_path)
    create_alias_file(alias_path=alias_path)

    print(f'Files created')


# -------------------------


@click.version_option(version=__version__)
@click.option(
    '--configuration',
    '-cfg',
    multiple=True,
    required=True,
    type=click.Path(exists=True, resolve_path=True, readable=True),
    help=("Path to the DUT configuration YAML Files. "
          "The YAML files should be specified (space separated) in the "
          "following  order "
          "1. isa_config.yaml "
          "2. core_config.yaml "
          "3. custom_config.yaml "
          "4. csr_grouping.yaml "
          "5. rv_debug.yaml"
          "The ordering should be strictly followed and any deviation will "
          "result in  UATG erroring out. This Parameter is needed to "
          "generate/validate tests and also generate covergroups"))
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
    """
        Parses the log generated upon test execution using regular expressions
        and provides a minimal coverage report.\n

        Required: -wd, --work_dir\n
                  -cfg, --configuration\n
                  -md, --module_dir\n
        Optional: -m, --modules (default - all)\n
                  -v, --verbose\n
    """
    logger.level(verbose)
    info(__version__)

    dut_dict = combine_config_yamls(configuration)

    module = clean_modules(module_dir, modules)
    validate_tests(modules=module,
                   work_dir=work_dir,
                   config_dict=dut_dict,
                   modules_dir=module_dir)

    logger.info(f'Exiting UATG')
    logger.info(f'Good day! Stay Hydrated.')
