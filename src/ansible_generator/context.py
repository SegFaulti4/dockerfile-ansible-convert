from src.shell.main import *
from src.utils import path_utils

import os.path
import jinja2
import jinja2.meta
from copy import deepcopy
from typing import Dict, Optional


class AnsiblePlayContext:
    global_env: Dict[str, str]
    local_env: Dict[str, str]
    facts: Dict[str, str]
    vars: Dict[str, str]
    global_user: Optional[str] = None
    local_user: Optional[str] = None

    workdir_local_vars: Dict[str, str]
    old_workdir_local_vars: Dict[str, str]

    WORKDIR_KEY = 'PWD'
    OLD_WORKDIR_KEY = 'OLDPWD'
    HOME_KEY = "HOME"

    def __init__(self, global_user: str, global_workdir: str):
        self.global_env = dict()
        self.local_env = dict()
        self.facts = dict()
        self.vars = dict()
        self.global_user = global_user
        self.local_user = None
        self.workdir_local_vars = dict()
        self.old_workdir_local_vars = dict()
        self.global_env[self.WORKDIR_KEY] = global_workdir
        self.global_env[self.HOME_KEY] = self.path_str_wrapper("~")

    def resolve_shell_word(self, word: ShellWordObject, strict: bool = True, empty_missing: bool = False,
                           override_local_env: Dict[str, str] = None) \
            -> Optional[Tuple[ShellWordObject, Dict[str, str]]]:
        if not word.parts:
            return word, {}

        value = ""
        parts = []
        local_vars = {}
        slice_start = 0
        for param in word.parts:
            param_name = param.name

            if override_local_env is not None:
                local_env = {**self.local_env, **override_local_env}
            else:
                local_env = self.local_env

            if param_name in local_env:
                local_var_name = self._local_var_name_wrapper(param_name)
                local_vars = {local_var_name: self.local_env[param_name]}
                param_name = local_var_name
                param_val = "{{ " + local_var_name + " }}"
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
            part = ShellParameter(name=param_name, pos=part_pos)
            parts.append(part)
            slice_start = param.pos[1]
        value += word.value[slice_start:]

        return ShellWordObject(value=value, parts=parts), local_vars

    def resolve_shell_command(self, command: ShellCommand, strict: bool = True, empty_missing: bool = False,
                              override_local_env: Dict[str, str] = None) \
            -> Optional[Tuple[List[ShellWordObject], Dict[str, str]]]:
        words = []
        local_vars = {}
        for part in command.words:
            resolved = self.resolve_shell_word(part, strict, empty_missing, override_local_env=override_local_env)
            if resolved is None:
                return None

            part_word, word_local_vars = resolved
            words.append(part_word)
            local_vars = {**local_vars, **word_local_vars}

        for var, val in self.workdir_local_vars.items():
            local_vars[var] = val
        return words, local_vars

    def resolve_shell_expression(self, expr: ShellExpression, strict: bool = True, empty_missing: bool = False) \
            -> Optional[str]:
        words: List[ShellWordObject] = []
        for part in expr.parts:
            if isinstance(part, ShellCommand):
                resolved = self.resolve_shell_command(part, strict, empty_missing)
                if resolved is None:
                    return None
                part_words, _ = resolved
                words.extend(part_words)
            else:
                return None

        return " ".join(word.value for word in words).strip('"')

    def get_environment(self):
        res = {**self.global_env, **self.local_env}
        # `PWD` env doesn't affect Ansible tasks
        if "PWD" in res:
            del res["PWD"]
        return res

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
        return self.global_env.get(self.WORKDIR_KEY, None)

    def get_local_workdir(self) -> Optional[str]:
        return self.local_env.get(self.WORKDIR_KEY, None)

    def get_global_old_workdir(self) -> Optional[str]:
        return self.global_env.get(self.OLD_WORKDIR_KEY, None)

    def get_local_old_workdir(self) -> Optional[str]:
        return self.local_env.get(self.OLD_WORKDIR_KEY, None)

    def set_global_old_workdir(self, value: str) -> None:
        self.global_env[self.WORKDIR_KEY] = value

    def set_local_old_workdir(self, value: str, local_vars: Optional[Dict[str, str]]) -> None:
        new_local_vars = dict() if local_vars is None else deepcopy(local_vars)
        self.local_env[self.WORKDIR_KEY] = value
        self.old_workdir_local_vars = new_local_vars

    def set_global_workdir(self, path: str, ignore_tilde: bool = False) -> None:
        self.set_global_old_workdir(self.get_global_workdir())
        self.global_env[self.WORKDIR_KEY] = self.path_str_wrapper(path, ignore_tilde=ignore_tilde)

    def set_local_workdir(self, path: str, local_vars: Optional[Dict[str, str]]) -> None:
        new_local_vars = dict() if local_vars is None else deepcopy(local_vars)
        self.set_local_old_workdir(self.get_local_workdir(), self.workdir_local_vars)
        self.local_env[self.WORKDIR_KEY] = self.path_str_wrapper(path)
        self.workdir_local_vars = new_local_vars

    def set_global_user(self, name: str) -> None:
        self.global_user = name
        self.global_env[self.HOME_KEY] = self.path_str_wrapper("~")

    def set_local_user(self, name: str) -> None:
        self.local_user = name
        self.local_env[self.HOME_KEY] = self.path_str_wrapper("~")

    def unset_local_user(self) -> None:
        self.local_user = None
        if self.HOME_KEY in self.local_env:
            del self.local_env[self.HOME_KEY]

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
        self.local_user = None
        self.old_workdir_local_vars.clear()
        self.workdir_local_vars.clear()

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

    def path_str_wrapper(self, path: str, override_user: str = None, ignore_tilde: bool = False) -> str:
        if override_user is None:
            usr = self.get_user()
        else:
            usr = override_user

        if self.get_workdir() is None:
            cwd = "/"
        else:
            cwd = self.get_workdir()

        return path_utils.path_str_wrapper(path, cwd=cwd, usr=usr, ignore_tilde=ignore_tilde)

    @staticmethod
    def _local_var_name_wrapper(name: str) -> str:
        return name.strip().lower().replace('-', '_') + "_local_var"
