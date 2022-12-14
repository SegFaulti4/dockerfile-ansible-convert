import dataclasses
from typing import Union, Dict, Optional

from src.shell.main import *


@dataclasses.dataclass
class TaskContext:
    cwd: str


class TaskMatcher:

    def match_command(self, comm: List[ShellWordObject], context: Optional[TaskContext] = None) \
            -> Union[Dict[str, str], None]:
        raise NotImplementedError
