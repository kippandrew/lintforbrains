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
