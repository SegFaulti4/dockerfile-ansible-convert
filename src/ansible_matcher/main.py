from typing import Union, Dict, Optional

from src.shell.main import *


class TaskMatcher:

    def match_command(self, comm: List[ShellWordObject], cwd: Optional[str] = None, usr: Optional[str] = None) \
            -> Union[Dict[str, str], None]:
        raise NotImplementedError
