from typing import Union, Dict

from libs.shell.main import *


class TaskMatcher:

    def match_command(self, comm: List[ShellWordObject]) -> Union[Dict[str, str], None]:
        raise NotImplementedError
