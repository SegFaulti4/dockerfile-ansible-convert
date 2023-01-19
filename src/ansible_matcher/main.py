from typing import Union, Dict, Optional

from src.shell.main import *
from src.ansible_matcher.statistics import *


class TaskMatcher:
    stats: TaskMatcherStatistics

    def match_command(self, comm: List[ShellWordObject], cwd: Optional[str] = None, usr: Optional[str] = None,
                      collect_stats: bool = False) \
            -> Union[Dict[str, str], None]:
        raise NotImplementedError
