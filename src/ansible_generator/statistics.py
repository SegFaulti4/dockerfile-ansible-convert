from typing import Type, List
from dataclasses import dataclass, field


@dataclass
class RoleGeneratorStatistics:
    names: List[str] = field(default_factory=list)
    coverages: List[float] = field(default_factory=list)
    lengths: List[int] = field(default_factory=list)


def unsupported_directive(func):
    def new_func(*args, **kwargs):
        d_type, d_cov, d_len = type(args[1]), 0., len(args[1])
        res = func(*args, **kwargs)

        args[0].stats.names.append(d_type.__name__)
        args[0].stats.coverages.append(d_cov)
        args[0].stats.lengths.append(d_len)
        return res

    return new_func


def supported_directive(func):
    def new_func(*args, **kwargs):
        d_type, d_cov, d_len = type(args[1]), 1., len(args[1])
        res = func(*args, **kwargs)

        args[0].stats.names.append(d_type.__name__)
        args[0].stats.coverages.append(d_cov)
        args[0].stats.lengths.append(d_len)
        return res

    return new_func
