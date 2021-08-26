import logging
import os
import sys

import click

import lintforbrains.config
import lintforbrains.inspect
import lintforbrains.logging
import lintforbrains.report
import lintforbrains.setup

_DEFAULT_PYTHON_PATH = '/usr/bin/python'
_DEFAULT_PYCHARM_VERSION = '2021.2'
_DEFAULT_PYCHARM_EDITION = 'community'
_DEFAULT_PROJECT_DIR = os.getenv('PROJECT_DIR', '.')

_LOG = lintforbrains.logging.getLogger(__name__)


def _enable_debug_logging():
    _configure_logging(logging.DEBUG)


def _enable_normal_logging():
    _configure_logging(logging.WARN)


def _configure_logging(level):
    # clear root handlers
    [logging.root.removeHandler(h) for h in logging.root.handlers]

    formatter = logging.Formatter(fmt='[%(asctime)s] [%(name)s] %(message)s')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.NOTSET)

    # configure root logger
    log = logging.getLogger('lintforbrains')
    log.addHandler(handler)
    log.setLevel(level)


@click.group()
@click.option('--debug/--no-debug', default=False, help="enable debug")
@click.pass_context
def cli(ctx, debug: bool):
    # configure logging
    if debug:
        _enable_debug_logging()
    else:
        _enable_normal_logging()


@cli.command()
@click.option('python_bin', '--python', type=str, default=_DEFAULT_PYTHON_PATH)
@click.option('pycharm_version', '--pycharm-version', type=str, default=_DEFAULT_PYCHARM_VERSION)
@click.option('pycharm_edition', '--pycharm-edition', type=str, default=_DEFAULT_PYCHARM_EDITION)
@click.pass_context
def setup(ctx, python_bin: str, pycharm_version: str, pycharm_edition: str):
    """
    Setup lintforbrains
    """
    return lintforbrains.setup.run_setup(pycharm_edition,
                                         pycharm_version,
                                         python_bin)


@cli.command()
@click.argument('project_dir', type=click.Path(exists=True), default='.')
@click.option('config_file', '--config', type=click.Path(exists=True), help="config file")
@click.pass_context
def inspect(ctx, project_dir: str, config_file: str):
    """
    Run inspection
    """
    ret = lintforbrains.inspect.run_inspect(project_dir, config_file)

    ctx.exit(ret)


@cli.command()
@click.argument('project_dir', type=click.Path(exists=True), default='.')
@click.option('config_file', '--config', type=click.Path(exists=True), help="config file")
@click.option('results_dir', '--results', type=click.Path(exists=True), help="results dir")
@click.pass_context
def report(ctx, project_dir: str, config_file: str, results_dir: str):
    """
    View inspection results
    """
    ret = lintforbrains.report.run_report(project_dir, config_file, results_dir)

    ctx.exit(ret)


if __name__ == "__main__":
    cli(obj=None, prog_name='lintforbrains')
