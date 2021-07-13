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
              help='Set to True if generated files needs to be cleaned.'
                   'Presently, __pycache__, tests/ folders are removed along '
                   'with yapsy-plugins',)
@click.option('--config_file',
              '-cf',
              multiple=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the yaml file containing DUT configuration. "
                   "Needed to generate/validate tests")
@click.option('--gen_test',
              '-gt',
              is_flag=True,
              help='Set to True if tests are to be generated. Else set it to '
                   'False. Generates ASM files and SV Files')
@click.option('--val_test',
              '-vt',
              is_flag=True,
              help='Set to True if generated tests are to be validated. Else '
                   'set it to False. Validates log files & SV cover-points',
              )
def cli(verbose, clean, config_file, gen_test, val_test):
    print(verbose, clean, config_file, gen_test, val_test)

    if clean:
        clean_dirs(verbose)

    if gen_test and config_file is not None:
        generate_tests(module='branch_predictor', inp=config_file,
                       verbose=verbose)

    if val_test and config_file is not None:
        validate_tests(module='branch_predictor', inp=config_file,
                       verbose=verbose)
        print('validated')
