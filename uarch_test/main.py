# See LICENSE.incore for details
"""Console script for uarch_tests."""

import click
import os
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
@click.option('--config_file',
              '-cf',
              multiple=False,
              type=click.Path(exists=True, resolve_path=True, readable=True),
              help="Path to the yaml file containing DUT configuration")
@click.option('--clean',
              '-cl',
              default='False',
              help='Set to True if generated files needs to be cleaned.'
                   'Presently, __pycache__, tests/ folders are removed along with '
                   'yapsy-plugins',
              type=click.Choice(['True', 'False'], case_sensitive=False))
@click.option('--gen_test',
              '-g',
              default='False',
              help='Set to True if tests are to be generated. Else set it to '
                   'False. Generates ASM files and SV Files',
              type=click.Choice(['True', 'False'], case_sensitive=False))
def cli(verbose, config_file, gen_test, clean):
    print(verbose, config_file, gen_test, clean)

    if clean == 'True' or clean == 'true':
        clean_dirs(verbose)
    if gen_test == 'True' or gen_test == 'true':
        generate_tests(module='branch_predictor', inp=config_file,
                       verbose=verbose)
