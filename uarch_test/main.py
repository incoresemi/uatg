# See LICENSE.incore for details
"""Console script for uarch_tests."""

import click
from uarch_test.log import logger
from uarch_test.test_generator import generate_tests, clean_dirs, validate_tests
from uarch_test.__init__ import __version__
from uarch_test.utils import clean_cli_params, list_of_modules


@click.command()
@click.version_option(prog_name="RISC-V Micro-Architectural Test Generator",
                      version=__version__)
@click.option('--verbose',
              '-v',
              default='debug',
              help='Set verbose level for debugging',
              type=click.Choice(['info', 'error', 'debug'],
                                case_sensitive=False))
@click.option(
    '--clean/--no_clean',
    '-cl/-no_cl',
    is_flag=True,
    help='clean flag is set if generated files needs to be cleaned.'
    'Presently, __pycache__, tests/ folders are removed along '
    'with yapsy-plugins',
)
@click.option('--config_file',
              '-cf',
              multiple=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the yaml file containing DUT configuration. "
              "Needed to generate/validate tests")
@click.option('--work_dir',
              '-wd',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the working directory where generated files will be"
              " stored.")
@click.option('--gen_test',
              '-gt',
              is_flag=True,
              help='gen_test flag is set if tests are to be generated. '
              'Generates ASM files and SV Files')
@click.option(
    '--val_test',
    '-vt',
    is_flag=True,
    help='val_test flag is set if generated tests are to be validated'
    '. Validates log files & SV cover-points',
)
@click.option(
    '--list_modules',
    '-lm',
    is_flag=True,
    help='displays all the modules that are presently supported by the '
    'framework',
)
@click.option('--linker_dir',
              '-ld',
              multiple=False,
              required=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the linkerfile.")
@click.option(
    '--module',
    '-m',
    default='all',
    multiple=False,
    is_flag=False,
    help="Enter a list of modules as a string in a comma separated "
    "format.\n--module 'branch_predictor, decoder'\nHere "
    "decoder and branch_predictor are chosen\nIf all module "
    "are to be selected use keyword 'all'.\n Presently supported"
    "modules are: branch_predictor",
    # TODO: find a proper way to list all modules and display them
    type=str)
def cli(verbose, clean, config_file, work_dir, module, gen_test, val_test,
        list_modules, linker_dir):
    logger.level(verbose)
    if list_modules:
        logger.debug('Module Options: ' + str(list_of_modules()))
    module, err = clean_cli_params(config_file=config_file,
                                   module=module,
                                   gen_test=gen_test,
                                   val_test=val_test)
    if err[0]:
        logger.error(err[1])
        exit(0)

    # cleaned parameters to be logged
    # logger.debug('verbose    : {0}'.format(verbose))
    # logger.debug('config_file: {0}'.format(config_file))
    # logger.debug('work_dir   : {0}'.format(work_dir))
    # logger.debug('module     : {0}'.format(module))
    # logger.debug('gen_test   : {0}'.format(gen_test))
    # logger.debug('val_test   : {0}'.format(val_test))
    # logger.debug('clean      : {0}'.format(clean))

    if gen_test:
        logger.debug('invoking gen_test')
        generate_tests(work_dir,
                       linker_dir,
                       modules=module,
                       inp=config_file,
                       verbose=verbose)
    if val_test:
        logger.debug('invoking val_test')
        validate_tests(modules=module,
                       inp=config_file,
                       work_dir=work_dir,
                       verbose=verbose)
    if clean:
        clean_dirs(work_dir=work_dir, verbose=verbose)
