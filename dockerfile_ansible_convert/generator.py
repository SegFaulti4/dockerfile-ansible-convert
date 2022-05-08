import dockerfile_ansible_convert.dockerfile_ast as dockerfile_ast
import dockerfile_ansible_convert.bash_parse as bash_ast
import dockerfile_ansible_convert.module_match as module_match

import exception as exception
from log import globalLog


class PlaybookContext:
    _global_vars = None
    _local_vars = None

    def __init__(self):
        self._global_vars = dict()
        self._local_vars = dict()

    def _var_value(self, name):
        return self._local_vars.get(name, self._global_vars.get(name))

    def resolve_parameterized_word(self, node):
        try:
            assert all(isinstance(p, bash_ast.ParameterNode) for p in node.parts)
            parts = sorted(node.parts, key=lambda x: x.pos[0], reverse=False)
            res = node.value[0:parts[0].pos[0]] + self._var_value(parts[0].name)
            for i in range(1, len(parts)):
                res += node.value[parts[i - 1].pos[1]:parts[i].pos[0]] + \
                    self._var_value(parts[i].name)
            return res
        except Exception as exc:
            globalLog.info(type(exc))
            globalLog.info(exc)
            raise exception.AnsibleContextException("Failed to resolve parameterized word")

    def add_global_var(self, name, value):
        self._global_vars[name] = value

    def add_local_var(self, name, value):
        self._local_vars[name] = value

    def clear_local_vars(self):
        self._local_vars.clear()

    def get_context(self):
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
            return self._rt_result
        except Exception as exc:
            globalLog.error(type(exc))
            globalLog.error(exc)
            globalLog.error("Failed to generate playbook from dockerfile AST on directive: " + str(self._rt_directive))

    def _last_task(self):
        return self._rt_result["tasks"][-1]

    def _new_register(self):
        self._rt_register_count += 1
        return 'auto_generated_register_' + str(self._rt_register_count)

    def _add_task(self, task, environment=True):
        self._rt_result["tasks"].append(task)
        if environment:
            self._add_environment_to_task(self._last_task())

    def _add_environment_to_task(self, task):
        context = self._context.get_context()
        if context:
            task["environment"] = context

    def _resolve_complex_value(self, value):
        self._add_task({
            'shell': {
                'cmd': 'echo "' + value + '"'
            }
        })

        self._last_task()["register"] = self._new_register()
        return '{{ ' + self._last_task()["register"] + ' }}'

    def _resolve_value(self, node):
        assert isinstance(node, bash_ast.WordNode)
        if node.type == bash_ast.WordNode.Type.CONST:
            return node.value
        if node.type == bash_ast.WordNode.Type.PARAMETERIZED:
            try:
                return self._context.resolve_parameterized_word(node)
            except exception.AnsibleContextException as exc:
                globalLog.debug(exc)
                globalLog.debug("Failed to resolve parameterized word, resolving as complex word")
                return self._resolve_complex_value(node.value)
        if node.type == bash_ast.WordNode.Type.COMPLEX:
            return self._resolve_complex_value(node.value)
        raise exception.PlaybookGeneratorException("Unknown WordNode type: " + node.type.value)

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
        }, environment=False)
        self._context.add_global_var(name=directive.name, value="{{ " + directive.name + "_fact }}")

    def _add_default_task(self, line):
        self._add_task({
            'shell': {
                'cmd': line
            }
        })

    def _handle_run(self, directive):
        self._context.clear_local_vars()
        if not directive.children:
            self._add_default_task(directive.line)
        else:
            _prev_type = ""
            for node in directive.children:
                _prev_type = getattr(self, "_handle_run_" + type(node).__name__.replace('Node', '').lower())\
                    (node, _prev_type)

    def _add_operator_condition_for_last_task(self, operator_type):
        if operator_type == "operatorand":
            self._last_task()["when"] = self._rt_result["tasks"][-2]["register"] + " is succeeded"
        elif operator_type == "operatoror":
            self._last_task()["when"] = self._rt_result["tasks"][-2]["register"] + " is not succeeded"

    def _handle_run_command(self, node, _prev_type):
        match = module_match.ModuleMatcher.match(self._resolve_value, node)
        if match is None:
            self._add_default_task(node.line)
        else:
            self._add_task(match)
        self._add_operator_condition_for_last_task(_prev_type)
        return "command"

    def _handle_run_assignment(self, node, _prev_type):
        prev_len = len(self._rt_result["tasks"])
        value = self._resolve_value(node.parts[0])
        self._context.add_local_var(name=node.name, value=value)
        if len(self._rt_result["tasks"]) > prev_len:
            self._add_operator_condition_for_last_task(_prev_type)
            return "command"
        return "assigmnent"

    def _handle_run_operatorand(self, node, _prev_type):
        if _prev_type == "command":
            self._last_task()["register"] = self._new_register()
        return "operatorand"

    def _handle_run_operatoror(self, node, _prev_type):
        if _prev_type == "command":
            self._last_task()["register"] = self._new_register()
        return "operatoror"

    def _handle_add(self, directive):
        self._handle_default(directive)

    def _handle_arg(self, directive):
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

    def _handle_user(self, directive):
        self._handle_default(directive)

    def _handle_volume(self, directive):
        self._handle_default(directive)

    def _handle_workdir(self, directive):
        self._handle_default(directive)


def generate_from_dockerfile(path):
    ast = dockerfile_ast.create_from_path(path)
    return PlaybookGenerator(ast=ast).generate()
