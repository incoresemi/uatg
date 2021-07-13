# See LICENSE.incore for details
"""Console script for uarch_tests."""

import click
from uarch_test.log import logger
from uarch_test.test_generator import generate_tests, clean_dirs, validate_tests
from uarch_test.__init__ import __version__


@click.command()
@click.version_option(prog_name="RISC-V Micro-Architectural Test Generator",
                      version=__version__)
@click.option('--verbose',
              '-v',
              default='error',
              help='Set verbose level for debugging',
              type=click.Choice(['info', 'error', 'debug'],
                                case_sensitive=False))
@click.option('--clean',
              '-cl',
              is_flag=True,
              help='clean flag is set if generated files needs to be cleaned.'
                   'Presently, __pycache__, tests/ folders are removed along '
                   'with yapsy-plugins', )
@click.option('--config_file',
              '-cf',
              multiple=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the yaml file containing DUT configuration. "
                   "Needed to generate/validate tests")
@click.option('--gen_test',
              '-gt',
              is_flag=True,
              help='gen_test flag is set if tests are to be generated. '
                   'Generates ASM files and SV Files')
@click.option('--val_test',
              '-vt',
              is_flag=True,
              help='val_test flag is set if generated tests are to be validated'
                   '. Validates log files & SV cover-points',
              )
@click.option('--module',
              '-m',
              default='branch_predictor',
              help="Select the module to generate tests. Use 'all' to "
                   "generate for all supported modules",
              type=click.Choice(['branch_predictor', 'all'],
                                case_sensitive=False))
def cli(verbose, clean, config_file, module, gen_test, val_test):
    logger.level(verbose)

    if (gen_test or val_test) and config_file is None:
        logger.error("config_file path is missing")
        exit(0)

    if gen_test:
        logger.debug('invoking gen_test')
        generate_tests(module=module, inp=config_file,
                       verbose=verbose)
    if val_test:
        logger.debug('invoking val_test')
        validate_tests(module=module, inp=config_file,
                       verbose=verbose)
    if clean:
        clean_dirs(verbose)
