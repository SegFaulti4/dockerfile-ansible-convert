from dataclasses import field
from typing import Any
from enum import Enum

from src.ansible_matcher.main import *
from src.dockerfile.main import *
from src.ansible_generator.context import *
from src.ansible_generator.statistics import *

from src.log import globalLog


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
    task_matcher: TaskMatcher
    stats: RoleGeneratorStatistics
    _df_content: DockerfileContent
    _context: Union[AnsiblePlayContext, None] = None
    _runtime: Union[_Runtime, None] = None

    def __init__(self, dc: DockerfileContent, tm: TaskMatcher):
        self._df_content = dc
        self.task_matcher = tm
        self.stats = RoleGeneratorStatistics(coverages=[])

    def generate(self) -> List[Dict[str, Any]]:
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

        self.stats = RoleGeneratorStatistics(coverages=[])
        self._runtime = _Runtime()
        self._context = AnsiblePlayContext(global_vars=dict(), local_vars=dict())
        for directive in self._df_content.directives:
            handle_map[type(directive)](directive)

        return self._return()

    ###################
    # GENERAL METHODS #
    ###################

    def _return(self):
        self._runtime.general.result_registers_num = 0
        self._runtime.general.echo_registers_num = 0
        self._runtime.local = _LocalRuntime()

        return self._runtime.general.role_tasks

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

    @supported_directive(RunDirective)
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

    @supported_directive(EnvDirective)
    def _handle_env(self, directive: EnvDirective) -> None:
        for name, value in zip(directive.names, directive.values):
            self._add_global_assignment(name, value)

    @supported_directive(ArgDirective)
    def _handle_arg(self, directive: ArgDirective) -> None:
        self._add_global_assignment(directive.name, directive.value)

    @supported_directive(UserDirective)
    def _handle_user(self, directive: UserDirective) -> None:
        val = self._context.resolve_shell_expression(directive.name)
        if val is None:
            task = self._create_echo_task(directive.name.line)
            register = self._add_echo_register(task)
            self._add_task(task, set_user=True, set_vars=False, set_condition=False)
            self._context.set_global_user("{{ " + register + " }}")
        else:
            self._context.set_global_user(name=val)

    @supported_directive(WorkdirDirective)
    def _handle_workdir(self, directive: WorkdirDirective) -> None:
        val = self._context.resolve_shell_expression(directive.path)
        if val is None:
            task = self._create_echo_task(directive.path.line)
            register = self._add_echo_register(task)
            self._add_task(task, set_user=True, set_vars=False, set_condition=False)
            self._context.set_global_workdir("{{ " + register + " }}")
        else:
            self._context.set_global_workdir(path=val)

    @supported_directive(AddDirective)
    def _handle_add(self, directive: AddDirective) -> None:
        paths = [directive.source] + [dest for dest in directive.destinations]
        vals = []
        for path in paths:
            val = self._context.resolve_shell_expression(path)
            if val is None:
                task = self._create_echo_task(path.line)
                register = self._add_echo_register(task)
                self._add_task(task, set_user=True, set_vars=False, set_condition=False)
                val = "{{ " + register + " }}"
            vals.append(val)

        for dest in vals[1:]:
            task = {
                "copy": {
                    "src": vals[0],
                    "dest": dest
                }
            }
            self._add_task(task, set_user=True, set_vars=False, set_condition=False)

    @supported_directive(CopyDirective)
    def _handle_copy(self, directive: CopyDirective) -> None:
        return self._handle_add(directive=AddDirective(source=directive.source,
                                                       destinations=directive.destinations))

    @unsupported_directive(FromDirective)
    def _handle_from(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(CmdDirective)
    def _handle_cmd(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(LabelDirective)
    def _handle_label(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(MaintainerDirective)
    def _handle_maintainer(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(ExposeDirective)
    def _handle_expose(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(EntrypointDirective)
    def _handle_entrypoint(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(VolumeDirective)
    def _handle_volume(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(OnbuildDirective)
    def _handle_onbuild(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(StopsignalDirective)
    def _handle_stopsignal(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(HealthcheckDirective)
    def _handle_healthcheck(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive(ShellDirective)
    def _handle_shell(self, directive) -> None:
        return self._handle_default(directive)

    #################################
    # ENV and ARG DIRECTIVE METHODS #
    #################################

    @staticmethod
    def _create_set_fact_task(fact_name: str, value: str) -> Dict[str, Any]:
        task = {
            "set_fact": {
                fact_name: value
            }
        }
        return task

    def _add_global_assignment(self, name: str, value: ShellExpression) -> None:
        val = self._context.resolve_shell_expression(value)
        if val is None:
            task = self._create_echo_task(value.line)
            register = self._add_echo_register(task)
            self._add_task(task, set_user=False, set_vars=False, set_condition=False)
            val = "{{ " + register + " }}"

        fact_name = self._context.global_var_name_wrapper(name)
        task = self._create_set_fact_task(fact_name=fact_name, value=val)

        self._add_task(task, set_user=False, set_vars=False, set_condition=False)
        self._context.set_global_var(name=name, value="{{ " + fact_name + " }}")

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

    def _add_task_user(self, task: Dict) -> None:
        user = self._context.get_user()
        if user is not None:
            task["become"] = True
            task["become_user"] = user

    def _add_task_vars(self, task: Dict) -> None:
        local_vars = self._context.get_local_vars()
        if local_vars:
            task["vars"] = local_vars

    def _create_shell_task(self, line: str) -> Dict[str, Any]:
        task = {
            "shell": {
                "cmd": line
            }
        }
        wd = self._context.get_workdir()
        if wd is not None:
            task["shell"]["chdir"] = wd

        return task

    @staticmethod
    def _create_echo_task(line: str) -> Dict[str, Any]:
        if not line.startswith('"') or not line.endswith('"'):
            line = '"' + line + '"'
        task = {
            "shell": {
                "cmd": "echo " + line
            }
        }

        return task

    def _clear_local_context(self) -> None:
        self._context.clear_local()
        self._runtime.local = _LocalRuntime()

    def _handle_run_shell(self, line: str) -> (_ScriptPartType, Any):
        task = self._create_shell_task(line)
        task = self._add_task(task, set_user=True, set_vars=True, set_condition=True)
        return _ScriptPartType.COMMAND, task

    def _handle_run_raw(self, obj: ShellRawObject) -> (_ScriptPartType, Any):
        return self._handle_run_shell(obj.value)

    def _handle_run_command(self, obj: ShellCommandObject) -> (_ScriptPartType, Any):
        words = self._context.resolve_shell_command(obj)
        if words is None:
            return self._handle_run_shell(obj.line)

        task = self.task_matcher.match_command(words,
                                               cwd=self._context.get_workdir(),
                                               usr=self._context.get_user())
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
