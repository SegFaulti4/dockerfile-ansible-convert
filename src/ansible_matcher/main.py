from typing import Union, Dict

from src.shell.main import *


class TaskMatcher:

    def match_command(self, comm: List[ShellWordObject]) -> Union[Dict[str, str], None]:
        raise NotImplementedError
