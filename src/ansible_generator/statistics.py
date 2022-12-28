from typing import Type, List, Tuple
from dataclasses import dataclass


@dataclass
class RoleGeneratorStatistics:
    coverages: List[Tuple[Type, float]]


def unsupported_directive(directive_type: Type):

    def decorator(func):
        def new_func(*args, **kwargs):
            res = func(*args, **kwargs)
            args[0].stats.coverages.append((directive_type, 0.))
            return res
        return new_func

    return decorator


def supported_directive(directive_type: Type):

    def decorator(func):
        def new_func(*args, **kwargs):
            res = func(*args, **kwargs)
            args[0].stats.coverages.append((directive_type, 1.))
            return res
        return new_func

    return decorator
