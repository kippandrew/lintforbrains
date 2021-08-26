import click

from lintforbrains import logging
from lintforbrains.inspect import run_inspect
from lintforbrains.report import run_report

_DEFAULT_PYTHON_PATH = '/usr/bin/python'
_DEFAULT_PYCHARM_VERSION = '2021.2'
_DEFAULT_PYCHARM_EDITION = 'community'

_LOG = logging.get_logger(__name__)


def _enable_debug_logging():
    logging.init_logger(logging.DEBUG)


def _enable_normal_logging():
    logging.init_logger(logging.WARN)


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
@click.option('python_bin', '--python', type=str, default=_DEFAULT_PYTHON_PATH)
@click.option('pycharm_version', '--pycharm-version', type=str, default=_DEFAULT_PYCHARM_VERSION)
@click.option('pycharm_edition', '--pycharm-edition', type=str, default=_DEFAULT_PYCHARM_EDITION)
def inspect(project_dir: str, config_file: str, python_bin: str, pycharm_version: str, pycharm_edition: str):
    """
    Run inspection
    """
    return run_inspect(project_dir,
                       config_file,
                       python_bin,
                       pycharm_edition,
                       pycharm_version)


@cli.command()
@click.argument('project_dir', type=click.Path(exists=True), default='.')
@click.option('config_file', '--config', type=click.Path(exists=True), help="config file")
@click.option('results_dir', '--results', type=click.Path(exists=True), help="results dir")
def report(project_dir: str, config_file: str, results_dir: str):
    """
    View inspection results
    """
    return run_report(project_dir, config_file, results_dir)


if __name__ == "__main__":
    cli(obj=None, prog_name='lintforbrains')
