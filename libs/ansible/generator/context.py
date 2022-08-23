from lib.shell.main import *

import re
from typing import Union, Dict
from dataclasses import dataclass


@dataclass
class AnsiblePlayContext:
    global_vars: Dict[str, str]
    local_vars: Dict[str, str]
    global_workdir = None
    local_workdir = None
    global_user = None
    local_user = None

    def path_str_wrapper(self, path: str):
        if re.fullmatch(r'\.(/.*)?', path):
            return self.get_workdir() + path[1:]
        if re.fullmatch(r'~(/.*)?', path):
            return "/home/" + self.get_user() + path[1:]
        return path

    def set_global_workdir(self, path: str) -> None:
        self.global_workdir = self.path_str_wrapper(path)

    def set_local_workdir(self, path: str) -> None:
        self.local_workdir = self.path_str_wrapper(path)

    def set_global_user(self, name: str) -> None:
        self.global_user = name

    def set_local_user(self, name: str) -> None:
        self.local_user = name

    def set_global_var(self, name: str, value: str) -> None:
        self.global_vars[name] = value

    def set_local_var(self, name: str, value: str) -> None:
        self.local_vars[name] = value

    def clear_local_context(self) -> None:
        self.local_vars.clear()

    def get_global_workdir(self) -> Union[str, None]:
        return self.global_workdir

    def get_local_workdir(self) -> Union[str, None]:
        return self.local_workdir

    def get_workdir(self) -> Union[str, None]:
        local_wd = self.get_local_workdir()
        if local_wd is None:
            return self.get_global_workdir()
        return local_wd

    def get_global_user(self) -> Union[str, None]:
        return self.global_user

    def get_local_user(self) -> Union[str, None]:
        return self.local_user

    def get_user(self) -> Union[str, None]:
        local_usr = self.get_local_user()
        if local_usr is None:
            return self.get_global_user()
        return local_usr

    def get_global_var(self, name):
        return self.global_vars.get(name, None)

    def get_local_var(self, name):
        return self.local_vars.get(name, None)

    def get_var(self, name):
        local_var = self.get_local_var(name)
        if local_var is None:
            return self.get_global_var(name)
        return local_var

    def get_vars(self):
        pass

    def resolve_shell_word(self, word: ShellWordObject):
        pass

    def resolve_shell_expression(self, expr: ShellExpression):
        pass
