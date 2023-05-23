from typing import List
from dataclasses import dataclass, field


@dataclass
class GeneratorStatisticsBase:
    name: List[str] = field(default_factory=list)
    supported: List[bool] = field(default_factory=list)
    coverage: List[float] = field(default_factory=list)
    length: List[int] = field(default_factory=list)
    stat_id: List[int] = field(default_factory=list)


@dataclass
class PlaybookGeneratorStatistics(GeneratorStatisticsBase):
    pass


@dataclass
class RunStatistics(GeneratorStatisticsBase):
    pass


def unsupported_directive(func):
    def new_func(*args, **kwargs):
        res = func(*args, **kwargs)

        stats = args[0].stats
        if args[0].collect_stats:
            stats.name.append(type(kwargs['directive']).__name__)
            stats.supported.append(False)
            stats.coverage.append(0.)
            stats.length.append(len(kwargs['directive']))
            stats.stat_id.append(args[0].stat_id)
        return res

    return new_func


def supported_directive(func):
    def new_func(*args, **kwargs):
        res = func(*args, **kwargs)

        stats = args[0].stats
        if args[0].collect_stats:
            stats.name.append(type(kwargs['directive']).__name__)
            stats.supported.append(True)
            stats.coverage.append(1.)
            stats.length.append(len(kwargs['directive']))
            stats.stat_id.append(args[0].stat_id)
        return res

    return new_func
