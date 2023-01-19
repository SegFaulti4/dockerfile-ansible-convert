from typing import Type, List
from dataclasses import dataclass, field


@dataclass
class TaskMatcherStatistics:
    name: List[str] = field(default_factory=list)
    supported: List[bool] = field(default_factory=list)
    coverage: List[float] = field(default_factory=list)
    length: List[int] = field(default_factory=list)
    line: List[str] = field(default_factory=list)
