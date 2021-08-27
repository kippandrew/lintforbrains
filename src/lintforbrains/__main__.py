import os
import shutil
import sys

import click

from lintforbrains import logging
from lintforbrains import config
from lintforbrains.inspect import run_inspect
from lintforbrains.report import run_report
from lintforbrains.utilities import abort

_DEFAULT_PYTHON_PATH = '/usr/bin/python'
_DEFAULT_PYCHARM_VERSION = '2021.2'
_DEFAULT_PYCHARM_EDITION = 'community'

_LOG = logging.get_logger(__name__)


def _enable_debug_logging():
    logging.init_logger(logging.DEBUG)


def _enable_normal_logging():
    logging.init_logger(logging.WARN)


# noinspection PyUnusedLocal
def _get_pycharm_home_dir(pycharm_version: str, pycharm_edition: str):
    """
    Return the path of PyCharm home directory
    """
    if sys.platform.lower() == 'linux':
        return '/opt/pycharm'
    else:
        raise NotImplementedError()


def _get_pycharm_config_dir(pycharm_version: str, pycharm_edition: str):
    """
    Return the path of PyCharm configuration directory
    """
    pycharm_name = "PyCharmCE" if pycharm_edition.lower() == "community" else "PyCharm"

    if sys.platform.lower() == 'linux':
        return os.path.expanduser(f"~/.config/JetBrains/{pycharm_name}{pycharm_version}")
    else:
        raise NotImplementedError()


def _get_python_bin():
    """
    Return the path of the Python binary
    """
    return shutil.which("python3") or shutil.which("python")


def _load_config(config_file: str):
    """
    Load the project configuration
    """
    try:
        return config.load_config(config_file)
    except FileNotFoundError:
        abort(f"Failed to load configuration file: {config_file}")


@click.group()
@click.option('--debug/--no-debug', default=False, help="enable debug")
def cli(debug: bool):
    # configure logging
    if debug:
        _enable_debug_logging()
    else:
        _enable_normal_logging()


@cli.command()
@click.argument('project_dir', type=click.Path(exists=True), default='.')
@click.option('config_file', '--config', type=click.Path(exists=True), help="config file")
@click.option('pycharm_version', '--pycharm-version', type=str, help="pycharm version")
@click.option('pycharm_edition', '--pycharm-edition', type=str, help="pycharm edition")
@click.option('pycharm_home_dir', '--pycharm-home-dir', type=str, help="pycharm home dir")
@click.option('pycharm_config_dir', '--pycharm-config-dir', type=str, help="pycharm config dir")
@click.option('python_bin', '--python', type=click.Path(exists=True), help="python binary path")
def inspect(project_dir: str, config_file: str, python_bin: str,
            pycharm_edition: str, pycharm_version: str, pycharm_home_dir: str, pycharm_config_dir: str):
    """
    Run code inspection
    """

    if not pycharm_version:
        pycharm_version = _DEFAULT_PYCHARM_VERSION

    if not pycharm_edition:
        pycharm_edition = _DEFAULT_PYCHARM_EDITION

    if not pycharm_home_dir:
        pycharm_home_dir = _get_pycharm_home_dir(pycharm_version, pycharm_edition)

    if not pycharm_config_dir:
        pycharm_config_dir = _get_pycharm_config_dir(pycharm_version, pycharm_edition)

    # load project config
    if config_file is None:
        config_file = os.path.join(project_dir, config.DEFAULT_CONFIG_FILE)
    project_config = _load_config(config_file)

    # run project inspection
    return run_inspect(project_dir,
                       project_config,
                       pycharm_version,
                       pycharm_edition,
                       pycharm_home_dir,
                       pycharm_config_dir,
                       python_bin or _get_python_bin(), debug_level=2)


@cli.command()
@click.argument('project_dir', type=click.Path(exists=True), default='.')
@click.option('config_file', '--config', type=click.Path(exists=True), help="config file")
@click.option('results_dir', '--results', type=click.Path(exists=True), help="results dir")
def report(project_dir: str, config_file: str, results_dir: str):
    """
    View inspection results
    """

    # load project config
    if config_file is None:
        config_file = os.path.join(project_dir, config.DEFAULT_CONFIG_FILE)
    project_config = _load_config(config_file)

    # generate report
    return run_report(project_dir,
                      project_config,
                      results_dir)


if __name__ == "__main__":
    cli(obj=None, prog_name='lintforbrains')
