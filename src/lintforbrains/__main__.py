import logging
import os
import sys

import click

import lintforbrains.config
import lintforbrains.inspect
import lintforbrains.results
import lintforbrains.runtime

_DEFAULT_PROJECT_DIR = os.getenv('PROJECT_DIR', '.')

_DEFAULT_CONFIG_FILE = '.lintconfig'


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


def _load_configuration(config_file):
    pass


@click.group()
@click.option('--debug/--no-debug', default=False, help="enable debug")
@click.pass_context
def cli(ctx, debug: bool):
    # configure logging
    if debug:
        _enable_debug_logging()
    else:
        _enable_normal_logging()

    # # load configuration
    # ctx.obj = lintforbrains.config.Configuration()
    # ctx.obj.read(os.path.join(config_file))


@cli.command()
@click.argument('config_dir', type=click.Path())
@click.option('--sdk', default="python", type=click.Path(exists=True))
@click.option('--sdk-name', default="Python SDK")
@click.option('--sdk-type', default="Python SDK")
def bootstrap(config_dir: str, sdk: str, sdk_name: str, sdk_type: str):
    """

    :return:
    """
    lintforbrains.runtime.configure_python_sdk(config_dir, sdk, sdk_name, sdk_type)


@cli.command()
@click.argument('project_dir', type=click.Path(exists=True), default='.')
def configure(project_dir: str):
    """

    :param project_dir:
    :return:
    """
    lintforbrains.runtime.configure_python_sdk('default', '3.6.5')


@cli.command()
@click.argument('project_dir', type=click.Path(exists=True), default='.')
def inspect(project_dir: str):
    """

    :param project_dir:
    :return:
    """
    inspection_config = lintforbrains.config.load_config(os.path.join(project_dir, _DEFAULT_CONFIG_FILE))

    inspection_results = lintforbrains.inspect.Inspection(project_dir, inspection_config).run(debug_level=2)

    for p in inspection_results.problems:
        print(p)


#
# @cli.command()
# @click.option('--project-dir', '-p', default=_DEFAULT_PROJECT_DIR, help='project directory')
# def report(results_dir: str):
#     results = lintforbrains.results.InspectionResults(results_dir)
#     for p in results.problems:
#         print(p)


if __name__ == "__main__":
    cli(obj=None, prog_name='lintforbrains')
