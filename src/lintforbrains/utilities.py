import os
import sys
import typing

import click


def abort(message: str, exit_code=1):
    click.echo(message)
    sys.exit(exit_code)


def substitute(input: str, substitutions: typing.Mapping[str, typing.Any]):
    for key, value in substitutions.items():
        input = input.replace(f"${key}$", value)
    return input


def jetbrains_config_path(pycharm_version: str, pycharm_edition: str):
    pycharm_name = "PyCharmCE" if pycharm_edition.lower() == 'community' else "PyCharm"

    if sys.platform.lower() == 'darwin':
        raise NotImplementedError()
    elif sys.platform.lower() == 'linux':
        return os.path.expanduser(f"~/.config/JetBrains/{pycharm_name}{pycharm_version}")
