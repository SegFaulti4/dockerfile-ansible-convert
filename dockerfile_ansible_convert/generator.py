import dockerfile_ansible_convert.dockerfile_ast as dockerfile_ast
import dockerfile_ansible_convert.bash_parse as bash_ast
import dockerfile_ansible_convert.module_match as module_match

import exception as exception
from log import globalLog


class PlaybookContext:
    _global_vars = None
    _local_vars = None
    _global_wd = None
    _local_wd = None
    _global_usr = None
    _local_usr = None

    def __init__(self):
        self._global_vars = dict()
        self._local_vars = dict()

    def _var_value(self, name):
        return self._local_vars.get(name, self._global_vars.get(name))

    def _set_assert(self, value):
        assert isinstance(value, str)

    def _resolve_parameterized_word(self, node):
        try:
            assert all(isinstance(p, bash_ast.ParameterNode) for p in node.parts)
            parts = sorted(node.parts, key=lambda x: x.pos[0], reverse=False)
            res = node.value[0:parts[0].pos[0]] + self._var_value(parts[0].name)
            for i in range(1, len(parts)):
                res += node.value[parts[i - 1].pos[1]:parts[i].pos[0]] + \
                       self._var_value(parts[i].name)
            res.strip('"')
            return res
        except Exception as exc:
            globalLog.info(type(exc))
            globalLog.info(exc)
            raise exception.PlaybookContextException("Failed to resolve parameterized word")

    def resolve_value(self, node):
        assert isinstance(node, bash_ast.WordNode)
        if node.type == bash_ast.WordNode.Type.CONST:
            res = node.value
            return res.strip('"')
        if node.type == bash_ast.WordNode.Type.PARAMETERIZED:
            try:
                return self._resolve_parameterized_word(node)
            except exception.PlaybookContextException as exc:
                globalLog.debug(exc)
                globalLog.debug("Failed to resolve parameterized word, resolving as complex word")
                return None
        if node.type == bash_ast.WordNode.Type.COMPLEX:
            return None
        raise exception.PlaybookContextException("Unknown WordNode type: " + node.type.value)

    def _concat_path_str(self, path_a, path_b):
        path_a.strip('"')
        path_b.strip('"')
        if not path_a.endswith('/'):
            path_a += '/'
        return path_a + path_b

    def resolve_path_str(self, path):
        path.strip('"')
        if path.startswith('/') or path.startswith('~'):
            return path
        if self._local_wd is not None:
            return self._concat_path_str(self._local_wd, path)
        if self._global_wd is not None:
            return self._concat_path_str(self._global_wd, path)
        return path

    def resolve_path_value(self, node):
        value = self.resolve_value(node)
        if value is None:
            return None
        return self.resolve_path_str(value)

    def set_global_wd(self, value):
        self._set_assert(value)
        value.strip('"')
        self._global_wd = self.resolve_path_str(value)

    def set_local_wd(self, value):
        self._set_assert(value)
        value.strip('"')
        self._local_wd = self.resolve_path_str(value)

    def set_global_usr(self, value):
        self._set_assert(value)
        value.strip('"')
        self._global_usr = value

    def set_local_usr(self, value):
        self._set_assert(value)
        value.strip('"')
        self._local_usr = value

    def add_global_var(self, name, value):
        self._set_assert(value)
        self._global_vars[name] = value

    def add_local_var(self, name, value):
        self._set_assert(value)
        self._local_vars[name] = value

    def clear_local_context(self):
        self._local_vars.clear()
        self._local_wd = None
        self._local_usr = None

    def get_user(self):
        if self._local_usr is not None:
            return self._local_usr
        return self._global_usr

    def get_wd(self):
        if self._local_wd is not None:
            return self._local_wd
        return self._global_wd

    def get_vars(self):
        var_names = set(list(self._global_vars.keys()) + list(self._local_vars.keys()))
        return {name: self._var_value(name) for name in var_names}


class PlaybookGenerator:
    _ast = None
    _context = None
    _rt_result = None
    _rt_register_count = 0

    _rt_directive = None

    def __init__(self, ast):
        assert ast is not None
        assert isinstance(ast, dockerfile_ast.AST)
        self._ast = ast

    def generate(self):
        try:
            self._context = PlaybookContext()
            self._rt_register_count = 0
            self._rt_result = {
                "hosts": "all",
                "name": "Generated from dockerfile",
                "tasks": list()
            }

            for directive in self._ast.directives:
                self._rt_directive = directive
                self._handle_directive(directive)

            _context = None
            return [self._rt_result]
        except Exception as exc:
            globalLog.error(type(exc))
            globalLog.error(exc)
            globalLog.error("Failed to generate playbook from dockerfile AST on directive: " + str(self._rt_directive))

    def _last_task(self):
        return self._rt_result["tasks"][-1]

    def _new_register(self):
        self._rt_register_count += 1
        return 'auto_generated_register_' + str(self._rt_register_count)

    def _add_task(self, task, context=True):
        self._rt_result["tasks"].append(task)
        if context:
            self._add_context_to_task(self._last_task())

    def _add_default_task(self, line):
        task = {
            'shell': {
                'cmd': line
            }
        }
        wd = self._context.get_wd()
        if wd is not None:
            task["shell"]["chdir"] = wd
        self._add_task(task)

    def _add_context_to_task(self, task):
        env_vars = self._context.get_vars()
        user = self._context.get_user()
        if env_vars:
            task["environment"] = env_vars
        if user is not None:
            task["become"] = True
            task["become_user"] = user

    def _resolve_complex_value(self, value):
        if not value.startswith('"') or not value.endswith('"'):
            value = '"' + value + '"'
        self._add_task({
            'shell': {
                'cmd': 'echo ' + value
            }
        })

        self._last_task()["register"] = self._new_register()
        return '{{ ' + self._last_task()["register"] + ' }}'

    def _resolve_value(self, node):
        value = self._context.resolve_value(node)
        if value is None:
            return self._resolve_complex_value(node.value)
        return value

    def _handle_directive(self, directive):
        getattr(self, "_handle_" + type(directive).__name__.replace('Node', '').lower())(directive)

    def _handle_default(self, directive):
        globalLog.info("Dockerfile AST node " + type(directive).__name__ + " doesn't affect playbook generation")

    def _handle_copy(self, directive):
        children = [self._resolve_value(v) for v in directive.children]
        for dest in children[1:]:
            self._add_task({
                'copy': {
                    'src': children[0],
                    'dest': dest
                }
            })

    def _handle_env(self, directive):
        value = self._resolve_value(directive.children[0])
        self._add_task({
            "set_fact": {
                directive.name + "_fact": value
            }
        }, context=False)
        self._context.add_global_var(name=directive.name, value="{{ " + directive.name + "_fact }}")

    def _handle_arg(self, directive):
        value = self._resolve_value(directive.children[0])
        self._add_task({
            "set_fact": {
                directive.name + "_fact": "{{ " + directive.name + " | default(" + value + ") }}"
            }
        }, context=False)
        self._context.add_global_var(name=directive.name, value="{{ " + directive.name + "_fact }}")

    def _handle_workdir(self, directive):
        value = self._resolve_value(directive.children[0])
        self._context.set_global_wd(value)

    def _handle_user(self, directive):
        value = self._resolve_value(directive.children[0])
        self._context.set_global_usr(value)

    def _handle_run(self, directive):
        if not directive.children:
            self._add_default_task(directive.line)
        else:
            _prev_type = ""
            for node in directive.children:
                _prev_type = getattr(self, "_handle_run_" + type(node).__name__.replace('Node', '').lower()) \
                    (node, _prev_type)
        self._context.clear_local_context()

    def _add_operator_condition_for_last_task(self, operator_type):
        if operator_type == "operatorand":
            self._last_task()["when"] = self._rt_result["tasks"][-2]["register"] + " is succeeded"
        elif operator_type == "operatoror":
            self._last_task()["when"] = self._rt_result["tasks"][-2]["register"] + " is not succeeded"
        elif operator_type == "true":
            pass
        elif operator_type == "false":
            self._last_task()["when"] = False

    def _handle_run_command(self, node, _prev_type):
        prev_len = len(self._rt_result["tasks"])

        match = module_match.ModuleMatcher.match(self._context, node)
        if match is None:
            self._add_default_task(node.line)
        else:
            self._add_task(match)

        if len(self._rt_result["tasks"]) > prev_len:
            self._add_operator_condition_for_last_task(_prev_type)
            return "command"
        return "idle"

    def _handle_run_assignment(self, node, _prev_type):
        prev_len = len(self._rt_result["tasks"])

        value = self._resolve_value(node.parts[0])
        self._context.add_local_var(name=node.name, value=value)

        if len(self._rt_result["tasks"]) > prev_len:
            self._add_operator_condition_for_last_task(_prev_type)
            return "command"
        return "idle"

    def _handle_run_operatorand(self, node, _prev_type):
        if _prev_type == "command":
            self._last_task()["register"] = self._new_register()
            return "operatorand"
        elif _prev_type == "idle":
            return "true"
        raise exception.PlaybookGeneratorException("Unknown type of previous command " + _prev_type)

    def _handle_run_operatoror(self, node, _prev_type):
        if _prev_type == "command":
            self._last_task()["register"] = self._new_register()
            return "operatoror"
        elif _prev_type == "idle":
            return "false"
        raise exception.PlaybookGeneratorException("Unknown type of previous command " + _prev_type)

    def _handle_add(self, directive):
        self._handle_default(directive)

    def _handle_cmd(self, directive):
        self._handle_default(directive)

    def _handle_entrypoint(self, directive):
        self._handle_default(directive)

    def _handle_expose(self, directive):
        self._handle_default(directive)

    def _handle_from(self, directive):
        self._handle_default(directive)

    def _handle_healthcheck(self, directive):
        self._handle_default(directive)

    def _handle_label(self, directive):
        self._handle_default(directive)

    def _handle_maintainer(self, directive):
        self._handle_default(directive)

    def _handle_onbuild(self, directive):
        self._handle_default(directive)

    def _handle_shell(self, directive):
        self._handle_default(directive)

    def _handle_stopsignal(self, directive):
        self._handle_default(directive)

    def _handle_volume(self, directive):
        self._handle_default(directive)


def generate_from_dockerfile(path):
    ast = dockerfile_ast.create_from_path(path)
    return PlaybookGenerator(ast=ast).generate()
