from enum import Enum
import itertools

from src.ansible_matcher.main import *
from src.containerfile.main import *
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
    collect_stats: bool
    default_user: str
    default_workdir: str
    stats: Optional[RoleGeneratorStatistics]
    matcher_tests: Optional[List[str]]

    _df_content: DockerfileContent
    _context: Union[AnsiblePlayContext, None] = None
    _runtime: Union[_Runtime, None] = None

    def __init__(self, dc: DockerfileContent, tm: TaskMatcher, default_user: str = "root", default_workdir: str = "/",
                 collect_stats: bool = False, collect_matcher_tests: bool = False):
        self._df_content = dc
        self.task_matcher = tm
        self.collect_stats = collect_stats
        self.collect_matcher_tests = collect_matcher_tests
        self.default_user = default_user
        self.default_workdir = default_workdir
        self.stats = None
        self.matcher_tests = None

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

        self.stats = RoleGeneratorStatistics()
        self.matcher_tests = list()
        self._runtime = _Runtime()
        self._context = AnsiblePlayContext(global_env=dict(), local_env=dict(),
                                           global_user=self.default_user,
                                           global_workdir=self.default_workdir,
                                           facts=dict(), vars=dict())
        for directive in self._df_content.directives:
            handle_map[type(directive)](directive=directive)

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
                  user: str = "",
                  variables: Dict[str, str] = None,
                  environment: Dict[str, str] = None,
                  set_condition: bool = False) -> Union[Dict, None]:
        if user:
            self._add_task_user(task, user)
        if variables:
            self._add_task_vars(task, variables)
        if environment:
            self._add_task_environment(task, environment)
        if set_condition:
            if self._set_task_condition(task):
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

    @staticmethod
    def _handle_default(directive) -> None:
        globalLog.info("Dockerfile directive " + type(directive).__name__ + " doesn't affect role generation")

    @supported_directive
    def _handle_run(self, directive: RunDirective) -> None:
        # method for each ShellScriptPart
        handle_run_map = {
            ShellRawObject: self._handle_run_command_raw,
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

    @supported_directive
    def _handle_env(self, directive: EnvDirective) -> None:
        for name, value in zip(directive.names, directive.values):
            fact_name = self._add_fact(name, value)
            self._context.add_global_env(name=name, value="{{ " + fact_name + " }}")

    @supported_directive
    def _handle_arg(self, directive: ArgDirective) -> None:
        name = directive.name
        fact_name = self._add_fact(name, directive.value)
        self._context.add_global_env(name=name, value="{{ " + fact_name + " }}")

    @supported_directive
    def _handle_user(self, directive: UserDirective) -> None:
        val = self._context.shell_expression_value(directive.name)
        if val is None:
            task = self._create_echo_task(directive.name.line)
            register = self._add_echo_register(task)
            self._add_task(task, user=self._context.get_user(), environment=self._context.get_environment(),
                           set_condition=False)
            self._context.set_global_user("{{ " + register + " }}")
        else:
            self._context.set_global_user(name=val)

    @supported_directive
    def _handle_workdir(self, directive: WorkdirDirective) -> None:
        val = self._context.shell_expression_value(directive.path, strict=False)
        if val is None:
            task = self._create_echo_task(directive.path.line)
            register = self._add_echo_register(task)
            self._add_task(task, user=self._context.get_user(), environment=self._context.get_environment(),
                           set_condition=False)

            path = "{{ " + register + "}}"
        else:
            path = val

        mkdir_task = self._create_mkdir_task(path)
        self._add_task(mkdir_task, user=self._context.get_user(), set_condition=False)
        self._context.set_global_workdir(path)

    @supported_directive
    def _handle_add(self, directive: AddDirective) -> None:
        paths = [directive.source] + [dest for dest in directive.destinations]
        vals = []
        for path in paths:
            val = self._context.shell_expression_value(path)
            if val is None:
                task = self._create_echo_task(path.line)
                register = self._add_echo_register(task)
                self._add_task(task, user=self._context.get_user(), environment=self._context.get_environment(),
                               set_condition=False)
                val = "{{ " + register + " }}"
            vals.append(val)

        for dest in vals[1:]:
            task = {
                "copy": {
                    "src": vals[0],
                    "dest": dest
                }
            }
            self._add_task(task, user=self._context.get_user(), set_condition=False)

    @supported_directive
    def _handle_copy(self, directive: CopyDirective) -> None:
        return self._handle_add(directive=AddDirective(source=directive.source,
                                                       destinations=directive.destinations))

    @unsupported_directive
    def _handle_from(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_cmd(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_label(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_maintainer(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_expose(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_entrypoint(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_volume(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_onbuild(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_stopsignal(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
    def _handle_healthcheck(self, directive) -> None:
        return self._handle_default(directive)

    @unsupported_directive
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

    @staticmethod
    def _create_etc_env_task(name: str, value: str) -> Dict[str, Any]:
        task = {
            "lineinfile": {
                "dest": "/etc/environment",
                "state": "present",
                "regexp": f"^{name}=",
                "line": f"{name}={value}"
            }
        }
        return task

    def _add_permanent_env(self, name: str, value: str):
        task = self._create_etc_env_task(name, value)
        task = self._add_task(task, set_condition=False)
        task["become"] = "yes"

    def _add_fact(self, name: str, value: ShellExpression) -> str:
        fact_name = name.strip().lower().replace('-', '_') + "_fact"
        val = self._context.shell_expression_value(value)
        if val is None:
            task = self._create_echo_task(value.line)
            register = self._add_echo_register(task)
            self._add_task(task, environment=self._context.get_environment(), set_condition=False)
            val = "{{ " + register + " }}"
        else:
            self._context.set_fact(fact_name, val)

        task = self._create_set_fact_task(fact_name=fact_name, value=val)
        self._add_task(task, set_condition=False)
        return fact_name

    #############################
    # WORKDIR DIRECTIVE METHODS #
    #############################

    @staticmethod
    def _create_mkdir_task(path: str) -> Dict:
        task = {
            "file": {
                "state": "directory",
                "path": path
            }
        }
        return task

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
    def _set_task_condition(self, task: Dict) -> bool:
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

    @staticmethod
    def _add_task_user(task: Dict, user: str) -> None:
        task["become"] = True
        if user != "root":
            task["become_user"] = user

    @staticmethod
    def _add_task_vars(task: Dict, local_vars: Dict[str, str]) -> None:
        task["vars"] = local_vars

    @staticmethod
    def _add_task_environment(task: Dict, environment: Dict[str, str]) -> None:
        task["environment"] = environment

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
        self._context.clear_local_context()
        self._runtime.local = _LocalRuntime()

    def _handle_run_command_raw(self, obj: ShellRawObject) -> (_ScriptPartType, Any):
        task = self._create_shell_task(obj.value)
        task = self._add_task(task, set_condition=True,
                              user=self._context.get_user(), environment=self._context.get_environment())
        return _ScriptPartType.COMMAND, task

    def _handle_run_command_shell(self, line: str, local_vars: Dict[str, str]) -> (_ScriptPartType, Any):
        task = self._create_shell_task(line)
        task = self._add_task(task, user=self._context.get_user(), variables=local_vars, set_condition=True)
        return _ScriptPartType.COMMAND, task

    def _handle_run_command(self, obj: ShellCommandObject) -> (_ScriptPartType, Any):
        resolved = self._context.resolve_shell_command(obj)

        if resolved is None:
            return self._handle_run_command_raw(ShellRawObject(value=obj.line))
        words, local_vars = resolved

        return self._handle_run_command_resolved(words=words, local_vars=local_vars)

    def _handle_run_command_resolved(self, words: List[ShellWordObject], local_vars: Dict[str, str],
                                     usr: str = None, cwd: str = None) -> (_ScriptPartType, Any):
        usr = self._context.get_user() if usr is None else usr
        cwd = self._context.get_workdir() if cwd is None else cwd
        line = " ".join(x.value for x in words)

        # ATTENTION: "collect_stats" parameter is passed to matcher
        # collected stats might then be altered `_handle_run_command_extracted`
        tasks = self.task_matcher.match_command(words, cwd=cwd, usr=usr, collect_stats=self.collect_stats)
        if tasks is not None:
            if self.collect_matcher_tests:
                values = [self._context.word_true_value(w) for w in words]
                if all(v is not None for v in values):
                    self.matcher_tests.append(" ".join(values))

            if len(tasks) == 1:
                task = self._add_task(tasks[0], user=usr, variables=local_vars, set_condition=True)
            else:
                task = self._add_task({"block": tasks}, user=usr, variables=local_vars, set_condition=True)
            return _ScriptPartType.COMMAND, task

        extracted_call = self.task_matcher.extract_command(words)
        if extracted_call is None:
            return self._handle_run_command_shell(line=line, local_vars=local_vars)
        return self._handle_run_command_extracted(extracted_call, local_vars, line)

    def _handle_run_command_extracted(self, extracted_call: ExtractedCommandCall,
                                      local_vars: Dict[str, str], line: str) -> (_ScriptPartType, Any):
        handle_map = {
            "sudo": self._handle_run_command_sudo,
            "cd": self._handle_run_command_cd
        }
        comm_name = extracted_call.params[0].value
        if comm_name not in handle_map:
            return self._handle_run_command_shell(line=line, local_vars=local_vars)
        return handle_map[comm_name](extracted_call, local_vars, line)

    def _handle_run_assignment(self, obj: ShellAssignmentObject) -> (_ScriptPartType, Any):
        value = self._context.shell_expression_value(obj.value)
        if value is None:
            task = self._create_echo_task(obj.value.line)
            register = self._add_echo_register(task)
            task = self._add_task(task, user=self._context.get_user(), environment=self._context.get_environment(),
                                  set_condition=True)
            self._context.add_local_env(name=obj.name, value="{{ " + register + " }}")

            return _ScriptPartType.COMMAND, task
        else:
            # example: `BAT=bruce || MAN=wayne; echo $BAT$MAN` in bash returns `bruce`
            # so in that case variable MAN should not be set
            if self._runtime.local.prev_part_type is not _ScriptPartType.OPERATOR_OR or \
                    self._runtime.local.prev_part_value is not None:
                self._context.set_var(name=obj.name, value=value)
                self._context.add_local_env(name=obj.name, value=value)

            return _ScriptPartType.NONE, None

    def _handle_run_operator_or(self, obj: ShellOperatorOrObject) -> (_ScriptPartType, Any):
        return _ScriptPartType.OPERATOR_OR, self._runtime.local.prev_part_value

    def _handle_run_operator_and(self, obj: ShellOperatorAndObject) -> (_ScriptPartType, Any):
        return _ScriptPartType.OPERATOR_AND, self._runtime.local.prev_part_value

    def _handle_run_operator_end(self, obj: ShellOperatorEndObject) -> (_ScriptPartType, Any):
        return _ScriptPartType.NONE, None

    ###################################
    # SPECIAL SHELL COMMANDS HANDLERS #
    ###################################

    def _handle_run_command_sudo(self, extracted_call: ExtractedCommandCall,
                                 local_vars: Dict[str, str], line: str) -> (_ScriptPartType, Any):
        params = extracted_call.params
        opt_words = []
        for p in params[1:]:
            if not p.value.startswith("-"):
                break
            opt_words.append(p.value)

        # length of `sudo` command doesn't include length of "sudoed" command
        if self.collect_stats:
            sudo_words = [params[0].value] + opt_words
            self.task_matcher.stats.length[-1] = sum(map(len, sudo_words)) + len(sudo_words) - 1

        # no `sudo` options are currently supported
        if opt_words:
            globalLog.info("No `sudo` options are currently supported - command is translated to shell")
            return self._handle_run_command_shell(line=line, local_vars=local_vars)

        # `sudo` command is covered, "sudoed" command might not be covered
        if self.collect_stats:
            self.task_matcher.stats.coverage[-1] = 1.0
        return self._handle_run_command_resolved(words=params[1:],
                                                 local_vars=local_vars, usr="root")

    def _handle_run_command_cd(self, extracted_call: ExtractedCommandCall,
                               local_vars: Dict[str, str], line: str) -> (_ScriptPartType, Any):
        if extracted_call.opts:
            globalLog.info("No `cd` options are currently supported - command is translated to shell")
            return self._handle_run_command_shell(line=line, local_vars=local_vars)

        if len(extracted_call.params) > 2:
            globalLog.info("More than one argument passed to `cd` - command is translated to shell")
            return self._handle_run_command_shell(line=line, local_vars=local_vars)

        # mark `cd` command as covered
        if self.collect_stats:
            self.task_matcher.stats.coverage[-1] = 1.
        self._context.set_local_workdir(extracted_call.params[1].value)
        return _ScriptPartType.NONE, None
