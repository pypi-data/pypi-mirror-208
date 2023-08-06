from typing_extensions import ParamSpec

P = ParamSpec('P')

__all__ = ['identity']

def identity(*args: P.args) -> P.args:
    return args