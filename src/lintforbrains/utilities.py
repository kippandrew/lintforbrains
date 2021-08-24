import typing


def substitute(input: str, substitutions: typing.Mapping[str, typing.Any]):
    for key, value in substitutions.items():
        input = input.replace(f"${key}$", value)
    return input
