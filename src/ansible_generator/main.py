from enum import Enum
import itertools
import validators

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


class _LocalRuntime:
    prev_part_type: _ScriptPartType
    prev_part_value: Union[Dict, None]

    def __init__(self):
        self.prev_part_type = _ScriptPartType.NONE
        self.prev_part_value = None


class _GeneralRuntime:
    role_tasks: List
    echo_registers_num: int
    result_registers_num: int

    def __init__(self):
        self.role_tasks = list()
        self.echo_registers_num = 0
        self.result_registers_num = 0


class _Runtime:
    general: _GeneralRuntime
    local: _LocalRuntime

    def __init__(self):
        self.general = _GeneralRuntime()
        self.local = _LocalRuntime()


class RoleGenerator:
    task_matcher: TaskMatcher
    default_user: str
    default_workdir: str

    stats: Optional[RoleGeneratorStatistics]
    matcher_tests: Optional[List[str]]

    # stat flags
    collect_stats: bool = False
    collect_matcher_tests: bool = False
    stat_id: int = -1

    _DEFAULT_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

    _df_content: DockerfileContent
    _context: Union[AnsiblePlayContext, None] = None
    _runtime: Union[_Runtime, None] = None

    def __init__(self, dc: DockerfileContent, tm: TaskMatcher, default_user: str = "root", default_workdir: str = "/"):
        self._df_content = dc
        self.task_matcher = tm
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
        self._add_default_context_vars()

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

    def _add_default_context_vars(self):
        default_vars = {
            "PATH": self._DEFAULT_PATH,
            "HOME": self._context.path_str_wrapper("~")
        }
        for name, value in default_vars.items():
            self._context.add_global_env(name, value)

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

    def _shell_expr_values(self, exps: List[ShellExpression], strict: bool = True, empty_missing: bool = False) \
            -> List[str]:
        res = []
        for expr in exps:
            val = self._context.resolve_shell_expression(expr, strict, empty_missing)
            if val is None:
                task = self._create_echo_task(expr.line)
                register = self._add_echo_register(task)
                self._add_task(task, user="root", environment=self._context.get_environment(), set_condition=False)
                res.append("{{ " + register + " }}")
            else:
                res.append(val)
        return res

    ###################
    # HANDLER METHODS #
    ###################

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
        fact_names = self._add_facts(directive.names, directive.values)
        for name, fact_name in zip(directive.names, fact_names):
            self._context.add_global_env(name=name, value="{{ " + fact_name + " }}")

    @supported_directive
    def _handle_arg(self, directive: ArgDirective) -> None:
        fact_name = self._add_fact(directive.name, directive.value)
        self._context.add_global_env(name=directive.name, value="{{ " + fact_name + " }}")

    @supported_directive
    def _handle_user(self, directive: UserDirective) -> None:
        name = self._shell_expr_values([directive.name], strict=False, empty_missing=True)[0]
        group = self._shell_expr_values([directive.group], strict=False, empty_missing=True)[0]

        task = {
            "user": {
                "name": name,
                "group": group if group else "root",
                "state": "present"
            }
        }
        self._add_task(task, set_condition=False)
        self._context.set_global_user(name=name)

    @supported_directive
    def _handle_workdir(self, directive: WorkdirDirective) -> None:
        path = self._shell_expr_values([directive.path], strict=False)[0]
        mkdir_task = self._create_mkdir_task(path)
        self._add_task(mkdir_task, user=self._context.get_user(), set_condition=False)
        self._context.set_global_workdir(path)

    @supported_directive
    def _handle_add(self, directive: AddDirective) -> None:
        sources, destination = self._prepare_sources_and_destination(directive)
        name, group = directive.chown_name.line, directive.chown_group.line

        urls, archives, files = [], [], []
        for source in sources:
            if self._is_url(source):
                urls.append(source)
            elif self._is_archive(source):
                archives.append(source)
            else:
                files.append(source)

        tasks = self._create_add_directive_tasks(urls, archives, files, destination, name=name, group=group)
        for task in tasks:
            self._add_task(task, user="root", set_condition=False)

    @supported_directive
    def _handle_copy(self, directive: CopyDirective) -> None:
        sources, destination = self._prepare_sources_and_destination(directive)
        name, group = directive.chown_name.line, directive.chown_group.line

        tasks = self._create_file_copy_tasks(sources, destination, name=name, group=group)
        for task in tasks:
            self._add_task(task, user="root", set_condition=False)

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
    def _fact_name_wrapper(s: str) -> str:
        fact_name = s.strip().lower().replace('-', '_') + "_fact"
        return fact_name

    def _define_fact(self, name: str, value: ShellExpression) -> Tuple[str, str]:
        fact_name = self._fact_name_wrapper(name)

        # self._shell_expr_values is not used
        # because behaviour depends on whether expression value
        # is available without calling of "echo" task
        val = self._context.resolve_shell_expression(value, strict=True)
        if val is None:
            task = self._create_echo_task(value.line)
            register = self._add_echo_register(task)
            self._add_task(task, environment=self._context.get_environment(), set_condition=False)
            val = "{{ " + register + " }}"
        else:
            self._context.set_fact(fact_name, val)
        return fact_name, val

    def _add_facts(self, names: List[str], values: List[ShellExpression]) -> List[str]:
        facts = {}
        for name, value in zip(names, values):
            fact_name, val = self._define_fact(name, value)
            facts[fact_name] = val
        task = {"set_fact": facts}
        self._add_task(task, set_condition=False)
        return list(facts.keys())

    def _add_fact(self, name: str, value: ShellExpression) -> str:
        return self._add_facts([name], [value])[0]

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

    ##################################
    # ADD and COPY DIRECTIVE METHODS #
    ##################################

    @staticmethod
    def _is_url(s: str) -> bool:
        return validators.url(s)

    @staticmethod
    def _is_archive(s: str) -> bool:
        ends = [".tar", ".tar.gz", ".tar.bz2", ".tar.xz"]
        return any(s.endswith(end) for end in ends)

    def _prepare_sources_and_destination(self, directive: Union[CopyDirective, AddDirective]) -> Tuple[List[str], str]:
        paths = [source for source in directive.sources] + [directive.destination]
        vals = self._shell_expr_values(paths, strict=True, empty_missing=True)
        vals = [self._context.path_str_wrapper(val) for val in vals]
        sources, destination = [v.rstrip("/") for v in vals[:-1]], vals[-1]
        return sources, destination

    @staticmethod
    def _create_file_copy_tasks(sources: List[str], destination: str,
                                name: str = "", group: str = "") -> List[Dict]:
        if not destination.endswith("/"):
            tasks = [
                {
                    "file": {
                        "state": "directory",
                        "path": "{{ dest | dirname }}"
                    },
                    "vars": {
                        "dest": destination
                    }
                },
                {
                    "copy": {
                        "src": "{{ item }}",
                        "dest": destination,
                        "mode": "0755",
                        "remote_src": False
                    },
                    "with_fileglob": sources
                }
            ]
            if name:
                tasks[-1]["copy"]["owner"] = name
            if group:
                tasks[-1]["copy"]["group"] = group
        else:
            tasks = [
                {
                    "stat": {
                        "path": "{{ item }}"
                    },
                    "with_fileglob": sources,
                    "register": "st_reg",
                    "delegate_to": "localhost"
                },
                {
                    "copy": {
                        "src": "{{ item.stat.path + '/' if ( item.stat.isdir is defined and item.stat.isdir ) else "
                               "item.stat.path }}",
                        "dest": destination,
                        "mode": "0755",
                        "remote_src": False
                    },
                    "loop": "{{ st_reg.results }}"
                }
            ]
            if name:
                tasks[-1]["copy"]["owner"] = name
            if group:
                tasks[-1]["copy"]["group"] = group
        return tasks

    @staticmethod
    def _create_url_copy_tasks(urls: List[str], destination: str,
                               name: str = "", group: str = "") -> List[Dict]:
        if not urls:
            return []

        if len(urls) > 1:
            tasks = [{
                "get_url": {
                    "url": "{{ item }}",
                    "decompress": False,
                    "dest": destination
                },
                "loop": urls
            }]
            if name:
                tasks[-1]["get_url"]["owner"] = name
            if group:
                tasks[-1]["get_url"]["group"] = group
        else:
            tasks = [{
                "get_url": {
                    "url": urls[0],
                    "decompress": False,
                    "dest": destination
                }
            }]
            if name:
                tasks[-1]["get_url"]["owner"] = name
            if group:
                tasks[-1]["get_url"]["group"] = group
        return tasks

    @staticmethod
    def _create_archive_copy_tasks(archives: List[str], destination: str,
                                   name: str = "", group: str = "") -> List[Dict]:
        if not archives:
            return []

        tasks = [
            {
                "file": {
                    "state": "directory",
                    "path": destination
                }
            },
            {
                "unarchive": {
                    "src": "{{ item }}",
                    "dest": destination,
                    "remote_src": False
                },
                "with_fileglob": archives
            }
        ]
        if name:
            tasks[-1]["unarchive"]["owner"] = name
        if group:
            tasks[-1]["unarchive"]["group"] = group
        return tasks

    @staticmethod
    def _create_add_directive_tasks(urls: List[str], archives: List[str],
                                    files: List[str], destination: str,
                                    name: str = "", group: str = "") -> List[Dict]:
        tasks = []
        tasks.extend(RoleGenerator._create_file_copy_tasks(files, destination, name=name, group=group))
        tasks.extend(RoleGenerator._create_url_copy_tasks(urls, destination, name=name, group=group))
        tasks.extend(RoleGenerator._create_archive_copy_tasks(archives, destination, name=name, group=group))
        return tasks

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

        tasks = self.task_matcher.match_command(words, cwd=cwd, usr=usr)
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
        # self._shell_expr_values is not used
        # because behaviour depends on whether expression value
        # is available without calling of "echo" task
        value = self._context.resolve_shell_expression(obj.value, strict=True)
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
        if self.task_matcher.collect_stats:
            sudo_words = [params[0].value] + opt_words
            self.task_matcher.stats.length[-1] = sum(map(len, sudo_words)) + len(sudo_words) - 1

        # no `sudo` options are currently supported
        if opt_words:
            globalLog.info("No `sudo` options are currently supported - command is translated to shell")
            return self._handle_run_command_shell(line=line, local_vars=local_vars)

        # `sudo` command is covered, "sudoed" command might not be covered
        if self.task_matcher.collect_stats:
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
        if self.task_matcher.collect_stats:
            self.task_matcher.stats.coverage[-1] = 1.
        if len(extracted_call.params) < 2:
            globalLog.info("No arguments for `cd` - command is skipped")
            return _ScriptPartType.NONE, None
        if extracted_call.params[1].value == '-':
            self._context.set_local_workdir(self._context.get_old_workdir())
            return _ScriptPartType.NONE, None
        self._context.set_local_workdir(extracted_call.params[1].value)
        return _ScriptPartType.NONE, None
