from typing import Type, List
from dataclasses import dataclass, field


@dataclass
class TaskMatcherStatistics:
    names: List[str] = field(default_factory=list)
    coverages: List[float] = field(default_factory=list)
    lengths: List[int] = field(default_factory=list)
