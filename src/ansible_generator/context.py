from src.shell.main import *

import os.path
import jinja2
import jinja2.meta
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class AnsiblePlayContext:
    global_env: Dict[str, str]
    local_env: Dict[str, str]
    facts: Dict[str, str]
    vars: Dict[str, str]
    global_workdir: Optional[str] = None
    local_workdir: Optional[str] = None
    global_user: Optional[str] = None
    local_user: Optional[str] = None
    global_old_workdir: Optional[str] = None
    local_old_workdir: Optional[str] = None

    _WORKDIR_KEY = 'PWD'
    _OLD_WORKDIR_KEY = 'OLDPWD'

    def resolve_shell_word(self, word: ShellWordObject, strict: bool = True, empty_missing: bool = False) \
            -> Optional[Tuple[ShellWordObject, Dict[str, str]]]:
        if not word.parts:
            return word, {}

        value = ""
        parts = []
        local_vars = {}
        slice_start = 0
        for param in word.parts:
            param_name = param.name
            if param_name in self.local_env:
                param_name = self._local_var_name_wrapper(param_name)
                param_val = "{{ " + param_name + " }}"
                local_vars = {param_name: param_val}
            elif param_name in self.global_env:
                param_val = self.global_env[param_name]
            elif strict:
                return None
            elif empty_missing:
                param_val = ""
            else:
                param_val = word.value[param.pos[0]:param.pos[1]]

            value += word.value[slice_start:param.pos[0]]
            part_pos = len(value), len(value) + len(param_val)
            value += param_val
            part = ShellParameterObject(name=param_name, pos=part_pos)
            parts.append(part)
            slice_start = param.pos[1]
        value += word.value[slice_start:]

        return ShellWordObject(value=value, parts=parts), local_vars

    def resolve_shell_command(self, command: ShellCommandObject, strict: bool = True, empty_missing: bool = False) \
            -> Optional[Tuple[List[ShellWordObject], Dict[str, str]]]:
        words = []
        local_vars = {}
        for part in command.parts:
            resolved = self.resolve_shell_word(part, strict, empty_missing)
            if resolved is None:
                return None

            part_word, word_local_vars = resolved
            words.append(part_word)
            local_vars = {**local_vars, **word_local_vars}

        return words, local_vars

    def resolve_shell_expression(self, expr: ShellExpression, strict: bool = True, empty_missing: bool = False) \
            -> Optional[str]:
        words: List[ShellWordObject] = []
        for part in expr.parts:
            if isinstance(part, ShellCommandObject):
                resolved = self.resolve_shell_command(part, strict, empty_missing)
                if resolved is None:
                    return None
                part_words, _ = resolved
                words.extend(part_words)
            else:
                return None

        return " ".join(word.value for word in words).strip('"')

    def get_environment(self):
        return {**self.global_env, **self.local_env}

    def get_user(self) -> Optional[str]:
        local_usr = self.get_local_user()
        if local_usr is None:
            return self.get_global_user()
        return local_usr

    def get_global_user(self) -> Optional[str]:
        return self.global_user

    def get_local_user(self) -> Optional[str]:
        return self.local_user

    def get_workdir(self) -> Optional[str]:
        local_wd = self.get_local_workdir()
        if local_wd is None:
            return self.get_global_workdir()
        return local_wd

    def get_old_workdir(self) -> Optional[str]:
        local_old_wd = self.get_local_old_workdir()
        if local_old_wd is None:
            return self.get_global_old_workdir()
        return local_old_wd

    def get_global_workdir(self) -> Optional[str]:
        return self.global_env.get(self._WORKDIR_KEY, None)

    def get_local_workdir(self) -> Optional[str]:
        return self.local_env.get(self._WORKDIR_KEY, None)

    def get_global_old_workdir(self) -> Optional[str]:
        return self.global_env.get(self._OLD_WORKDIR_KEY, None)

    def get_local_old_workdir(self) -> Optional[str]:
        return self.local_env.get(self._OLD_WORKDIR_KEY, None)

    def set_global_old_workdir(self, value: str) -> None:
        self.global_env[self._WORKDIR_KEY] = value

    def set_local_old_workdir(self, value: str) -> None:
        self.local_env[self._WORKDIR_KEY] = value

    def set_global_workdir(self, path: str) -> None:
        self.set_global_old_workdir(self.get_global_workdir())
        self.global_env[self._WORKDIR_KEY] = self.path_str_wrapper(path)

    def set_local_workdir(self, path: str) -> None:
        self.set_local_old_workdir(self.get_local_workdir())
        self.local_env[self._WORKDIR_KEY] = self.path_str_wrapper(path)

    def set_global_user(self, name: str) -> None:
        self.global_user = name

    def add_global_env(self, name: str, value: str) -> None:
        self.global_env[name] = value

    def add_local_env(self, name: str, value: str) -> None:
        self.local_env[name] = value

    # only for detection of true global var value
    # useful for matcher tests collection
    def set_fact(self, name: str, value: str) -> None:
        val = self._str_true_value(value)
        if val is not None:
            self.facts[name] = val

    # only for detection of true local var value
    # useful for matcher tests collection
    def set_var(self, name: str, value: str) -> None:
        val = self._str_true_value(value)
        if val is not None:
            self.vars[name] = val

    def clear_local_context(self) -> None:
        self.local_env.clear()
        self.vars.clear()
        self.local_workdir = None
        self.local_user = None

    def word_true_value(self, word: ShellWordObject) -> Optional[str]:
        return self._str_true_value(word.value)

    def _str_true_value(self, value: str) -> Optional[str]:
        # Kudos to https://stackoverflow.com/a/55699590
        env = jinja2.Environment(undefined=jinja2.DebugUndefined)
        template = env.from_string(value)
        rendered = template.render({**self.facts, **self.vars})

        ast = env.parse(rendered)
        undefined = jinja2.meta.find_undeclared_variables(ast)

        if undefined:
            return None
        return rendered

    def path_str_wrapper(self, path: str) -> str:
        if path.startswith("~"):
            path = "/home/" + self.get_user() + path[1:]
        workdir = self.get_workdir()
        if workdir is None:
            workdir = "/"
        return os.path.join(workdir, path)

    @staticmethod
    def _local_var_name_wrapper(name: str) -> str:
        return name.strip().lower().replace('-', '_')
