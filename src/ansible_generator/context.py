from src.shell.main import *

import re
from typing import Union, Dict, Optional
from dataclasses import dataclass


@dataclass
class AnsiblePlayContext:
    global_vars: Dict[str, str]
    local_vars: Dict[str, str]
    global_env: Dict[str, str]
    local_env: Dict[str, str]
    global_workdir: Union[str, None] = None
    local_workdir: Union[str, None] = None
    global_user: Union[str, None] = None
    local_user: Union[str, None] = None

    def resolve_shell_word(self, word: ShellWordObject) -> Optional[Tuple[ShellWordObject, Dict[str, str]]]:
        if not word.parts:
            return word, {}

        value = ""
        parts = []
        local_vars = {}
        slice_start = 0
        for param in word.parts:
            param_name = param.name
            if param_name in self.local_vars:
                param_name = self._local_var_name_wrapper(param_name)
                param_val = "{{ " + param_name + " }}"
                local_vars = {param_name: param_val}
            elif param_name in self.global_vars:
                param_val = self.global_vars[param_name]
            else:
                return None

            value += word.value[slice_start:param.pos[0]]
            part_pos = len(value), len(value) + len(param_val)
            value += param_val
            part = ShellParameterObject(name=param_name, pos=part_pos)
            parts.append(part)
            slice_start = param.pos[1]
        value += word.value[slice_start:]

        return ShellWordObject(value=value, parts=parts), local_vars

    def resolve_shell_command(self, command: ShellCommandObject) \
            -> Optional[Tuple[List[ShellWordObject], Dict[str, str]]]:
        # every ParameterNode should be rewritten
        # as a reference of ansible variable
        words = []
        local_vars = {}
        for word in command.parts:
            resolved = self.resolve_shell_word(word)
            if resolved is None:
                return None

            word, loc_vars = resolved
            words.append(word)
            local_vars = {**local_vars, **loc_vars}

        return words, local_vars

    def resolve_shell_expression(self, expr: ShellExpression) -> Optional[str]:
        words: List[ShellWordObject] = []
        for part in expr.parts:
            if isinstance(part, ShellCommandObject):
                for word in part.parts:
                    if isinstance(word, ShellWordObject):
                        resolved = self.resolve_shell_word(word)
                        if resolved is None:
                            return None
                        else:
                            word, _ = resolved
                            words.append(word)
                    else:
                        return None
            else:
                return None

        return " ".join(word.value for word in words)

    def get_environment(self):
        return {**self.global_env, **self.local_env}

    def get_workdir(self) -> Union[str, None]:
        local_wd = self.get_local_workdir()
        if local_wd is None:
            return self.get_global_workdir()
        return local_wd

    def get_global_workdir(self) -> Union[str, None]:
        return self.global_workdir

    def get_local_workdir(self) -> Union[str, None]:
        return self.local_workdir

    def get_user(self) -> Union[str, None]:
        local_usr = self.get_local_user()
        if local_usr is None:
            return self.get_global_user()
        return local_usr

    def get_global_user(self) -> Union[str, None]:
        return self.global_user

    def get_local_user(self) -> Union[str, None]:
        return self.local_user

    def has_global_var(self, name: str) -> bool:
        return name in self.global_vars

    def has_global_env_var(self, name: str) -> Optional[str]:
        return self.global_env.get(name, None)

    def set_global_workdir(self, path: str) -> None:
        self.global_workdir = self._path_str_wrapper(path)

    def set_global_user(self, name: str) -> None:
        self.global_user = name

    def set_local_workdir(self, path: str) -> None:
        self.local_workdir = self._path_str_wrapper(path)

    def add_global_var(self, name: str, value: str) -> None:
        self.global_vars[name] = value

    def add_local_var(self, name: str, value: str) -> None:
        self.local_vars[name] = value

    def add_global_env_var(self, name: str, value: str) -> None:
        self.global_env[name] = value

    def add_local_env_var(self, name: str, value: str) -> None:
        self.local_env[name] = value

    def clear_local_context(self) -> None:
        self.local_vars.clear()
        self.local_env.clear()
        self.local_workdir = None
        self.local_user = None

    def del_global_env_var(self, name: str) -> None:
        if name in self.global_env:
            del self.global_env[name]

    def _path_str_wrapper(self, path: str) -> str:
        if re.fullmatch(r'\.(/.*)?', path):
            return self.get_workdir() + path[1:]
        if re.fullmatch(r'~(/.*)?', path):
            return "/home/" + self.get_user() + path[1:]
        return path

    @staticmethod
    def _local_var_name_wrapper(name: str) -> str:
        return name.strip().lower().replace('-', '_')
