# See LICENSE.incore for details
"""Console script for uarch_tests."""

import click
import os

from uarch_test.log import logger
from uarch_test.test_generator import load_yaml
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
@click.option('--gen_test',
              '-g',
              default='False',
              help='Set to True if tests are to be generated. Else set it to '
              'False',
              type=click.Choice(['True', 'False'], case_sensitive=False))
def cli(verbose, config_file, gen_test):
    yaml = load_yaml(config_file)
    print(yaml)
