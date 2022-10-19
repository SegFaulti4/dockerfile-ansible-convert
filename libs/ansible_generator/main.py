from dataclasses import field
from typing import Any
from enum import Enum

from libs.ansible_matcher.main import *
from libs.dockerfile.main import *
from libs.ansible_generator.context import *

from log import globalLog


class _ScriptPartType(Enum):
    OPERATOR_OR = 1
    OPERATOR_AND = 2
    COMMAND = 3
    NONE = 4


@dataclass
class _LocalRuntime:
    prev_part_type: _ScriptPartType = None
    prev_part_value: Union[Dict, None] = None


@dataclass
class _GeneralRuntime:
    # directive: DockerfileDirective = None
    role_tasks: List = field(default_factory=list)
    echo_registers_num: int = 0
    result_registers_num: int = 0


@dataclass
class _Runtime:
    general: _GeneralRuntime = _GeneralRuntime()
    local: _LocalRuntime = _LocalRuntime()


class RoleGenerator:
    _df_content: DockerfileContent = None
    _context: AnsiblePlayContext = None
    _runtime: _Runtime = None
    _task_matcher: TaskMatcher = None

    def __init__(self, dc: DockerfileContent, tm):
        self._df_content = dc
        self._task_matcher = tm

    def generate(self):
        # method for each DockerfileDirective
        handle_map = {
            RunDirective: self._handle_run,
            EnvDirective: self._handle_env,
            ArgDirective: self._handle_arg,
            UserDirective: self._handle_user,
            WorkdirDirective: self._handle_workdir,
            AddDirective: self._handle_add,
            CopyDirective: self._handle_copy,
            FromDirective: self._handle_from,
            CmdDirective: self._handle_cmd,
            LabelDirective: self._handle_label,
            MaintainerDirective: self._handle_maintainer,
            ExposeDirective: self._handle_expose,
            EntrypointDirective: self._handle_entrypoint,
            VolumeDirective: self._handle_volume,
            OnbuildDirective: self._handle_onbuild,
            StopsignalDirective: self._handle_stopsignal,
            HealthcheckDirective: self._handle_healthcheck,
            ShellDirective: self._handle_shell
        }

        self._runtime = _Runtime()
        self._context = AnsiblePlayContext(global_vars=dict(), local_vars=dict())
        for directive in self._df_content.directives:
            handle_map[type(directive)](directive)

        # TODO
        return self._return()

    ###################
    # GENERAL METHODS #
    ###################

    def _add_task(self, task: Dict,
                  set_user: bool,
                  set_vars: bool,
                  set_condition: bool) -> Union[Dict, None]:
        if set_user:
            self._add_task_user(task)
        if set_vars:
            self._add_task_vars(task)
        if set_condition:
            if self._add_task_condition(task):
                self._runtime.general.role_tasks.append(task)
                return self._runtime.general.role_tasks[-1]
            else:
                return None

        self._runtime.general.role_tasks.append(task)
        return self._runtime.general.role_tasks[-1]

    ###################
    # HANDLER METHODS #
    ###################

    # def _handle_directive(self, directive: DockerfileDirective) -> None:
    #    getattr(self, "_handle_" + type(directive).__name__.replace('Node', '').lower())(directive)

    def _handle_default(self, directive) -> None:
        globalLog.info("Dockerfile directive " + type(directive).__name__ + " doesn't affect role generation")

    def _handle_run(self, directive: RunDirective) -> None:
        # method for each ShellScriptPart
        handle_run_map = {
            ShellRawObject: self._handle_run_raw,
            ShellCommandObject: self._handle_run_command,
            ShellAssignmentObject: self._handle_run_assignment,
            ShellOperatorOrObject: self._handle_run_operator_or,
            ShellOperatorAndObject: self._handle_run_operator_and,
            ShellOperatorEndObject: self._handle_run_operator_end
        }

        for obj in directive.script.parts:
            part_type, part_value = handle_run_map[type(obj)](obj=obj)
            self._runtime.local.prev_part_type = part_type
            self._runtime.local.prev_part_value = part_value

        self._clear_local_context()

    #########################
    # RUN DIRECTIVE METHODS #
    #########################

    def _add_result_register(self, task: Dict) -> str:
        register = "result_register_" + str(self._runtime.general.result_registers_num)
        task["register"] = register

        self._runtime.general.result_registers_num += 1
        return register

    def _add_echo_register(self, task: Dict) -> str:
        register = "echo_register_" + str(self._runtime.general.echo_registers_num)
        task["register"] = register

        self._runtime.general.echo_registers_num += 1
        return register

    # returns True if task with set condition should be added and False otherwise
    def _add_task_condition(self, task: Dict) -> bool:
        if self._runtime.local.prev_part_type is _ScriptPartType.OPERATOR_OR:
            prev_task = self._runtime.local.prev_part_value
            if prev_task is not None:
                register = self._add_result_register(prev_task)
                task["when"] = register + " is not succeeded"
                return True
            else:
                # if prev_task is None that means
                # that previous part of script cannot fail
                # so new task will never be executed
                return False
        elif self._runtime.local.prev_part_type is _ScriptPartType.OPERATOR_AND:
            prev_task = self._runtime.local.prev_part_value
            if prev_task is not None:
                register = self._add_result_register(prev_task)
                task["when"] = register + " is succeeded"
                return True
            return True
        else:
            return True

    def _add_task_user(self, task: Dict):
        user = self._context.get_user()
        if user is not None:
            task["become"] = True
            task["become_user"] = user

    def _add_task_vars(self, task: Dict):
        local_vars = self._context.get_local_vars()
        if local_vars:
            task["vars"] = local_vars

    def _create_shell_task(self, line: str):
        task = {
            "shell": {
                "cmd": line
            }
        }
        wd = self._context.get_workdir()
        if wd is not None:
            task["shell"]["chdir"] = wd

        return task

    def _create_echo_task(self, line: str):
        if not line.startswith('"') or not line.endswith('"'):
            line = '"' + line + '"'
        task = {
            "shell": {
                "cmd": "echo " + line
            }
        }

        return task

    def _clear_local_context(self):
        self._context.clear_local()
        self._runtime.local = _LocalRuntime()

    def _handle_run_shell(self, line: str) -> (_ScriptPartType, Any):
        task = self._create_shell_task(line)
        task = self._add_task(task, set_user=True, set_vars=True, set_condition=True)
        return _ScriptPartType.COMMAND, task

    def _handle_run_raw(self, obj: ShellRawObject) -> (_ScriptPartType, Any):
        return self._handle_run_shell(obj.value)

    def _handle_run_command(self, obj: ShellCommandObject) -> (_ScriptPartType, Any):
        command = self._context.resolve_shell_command(obj)
        if command is None:
            return self._handle_run_shell(obj.line)

        task = self._task_matcher.match_command(command.parts)
        if task is None:
            return self._handle_run_shell(obj.line)

        task = self._add_task(task, set_user=True, set_vars=True, set_condition=True)
        return _ScriptPartType.COMMAND, task

    def _handle_run_assignment(self, obj: ShellAssignmentObject) -> (_ScriptPartType, Any):
        value = self._context.resolve_shell_expression(obj.value)
        if value is None:
            task = self._create_echo_task(obj.value.line)
            register = self._add_echo_register(task)
            task = self._add_task(task, set_user=True, set_vars=True, set_condition=True)
            # might need another method for that
            self._context.set_local_var(name=obj.name, value="{{ " + register + " }}")

            return _ScriptPartType.COMMAND, task
        else:
            # example: `BAT=bruce || MAN=wayne; echo $BAT$MAN` returns `bruce`
            # so in that case variable MAN should not be set
            if self._runtime.local.prev_part_type is not _ScriptPartType.OPERATOR_OR or \
                    self._runtime.local.prev_part_value is not None:
                self._context.set_local_var(name=obj.name, value=value)

            return _ScriptPartType.NONE, None

    def _handle_run_operator_or(self, obj: ShellOperatorOrObject) -> (_ScriptPartType, Any):
        return _ScriptPartType.OPERATOR_OR, self._runtime.local.prev_part_value

    def _handle_run_operator_and(self, obj: ShellOperatorAndObject) -> (_ScriptPartType, Any):
        return _ScriptPartType.OPERATOR_AND, self._runtime.local.prev_part_value

    def _handle_run_operator_end(self, obj: ShellOperatorEndObject) -> (_ScriptPartType, Any):
        return _ScriptPartType.NONE, None
