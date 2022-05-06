from enum import Enum
from dataclasses import dataclass

import docker2ansible.dockerfile_ast.enrich_config as enrich_config
import docker2ansible.dockerfile_ast.ast as ast
import docker2ansible.dockerfile_ast.bash as ast_bash
from docker2ansible.dockerfile_ast._meta import MetaSingleton
from docker2ansible import exception
from docker2ansible.log import globalLog


@dataclass
class EnrichedCommand(ast.Node):

    params = {}
    opts = {}

    def __init__(self):
        pass

    def _process(self):
        pass


class _CommandScenario:
    command_name = None
    scenario_name = None
    _requires = []
    _map_opts = {}

    _rt_result = None
    _rt_comm_list = None
    _rt_require = None
    _rt_skip_opts = None
    _rt_opts = []

    class _CommandRequirement:

        class Type(Enum):
            STRICT_CONSTANT = "strict_constant"
            STRICT_ABSTRACT = "strict_abstract"
            OPTIONAL_ABSTRACT = "optional_abstract"
            OPTIONAL_ABSTRACT_LIST = "optional_abstract_list"

        type = Type.STRICT_CONSTANT
        value = ""

        def __init__(self, req_str):
            # TODO
            pass

    class _CommandOpt:

        arg_required = False
        many_args = False
        name = ""

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def __init__(self, command_name, config):
        """
        {
            'name': str,
            'cmd': str,
            'opts': {
                opt_str: {'name': str, 'arg_required': bool, 'many_args': bool},
                ...
            }
        {
        """
        self.command_name = command_name
        self.scenario_name = config['name']
        self._requires = [_CommandScenario._CommandRequirement(req_str) for req_str in config['cmd'].split()]
        self._map_opts = {k: _CommandScenario._CommandOpt(**config['map_opts'][k]) for k in config['opts']}

    def probe(self, comm):
        try:
            self._rt_result = EnrichedCommand()
            self._rt_comm_list = comm.children.copy()
            self._rt_skip_opts = False

            for require in self._requires:
                self._rt_require = require
                if not getattr(self, "_probe_" + require.type.value)():
                    self._rt_result = None
                    return self._return()

            self._probe_opts()

            if self._rt_comm_list:
                raise exception.EnrichCommandException('Excessive arguments provided')
            return self._rt_result

        except ValueError as exc:
            globalLog.info(exc)
            self._rt_result = None
            return self._return()
        except KeyError as exc:
            globalLog.info(exc)
            self._rt_result = None
            return self._return()
        except exception.EnrichCommandException as exc:
            globalLog.info(exc)
            globalLog.info(comm['line'])
            self._rt_result = None
            return self._return()

    def _return(self):
        # TODO
        # transform opts
        self._rt_comm_list = None
        self._rt_require = None
        self._rt_skip_opts = None
        return self._rt_result

    def _probe_strict_constant(self):
        if self._rt_comm_list:
            node = self._rt_comm_list[0]
            if isinstance(node, ast_bash.PlainWordNode) and node.value == self._rt_require.value:
                self._rt_comm_list.pop(0)
                return
        raise exception.EnrichCommandException("Strict constant requirement " + self._rt_require.value +
                                               " is not satisfied")

    def _probe_strict_abstract(self):
        self._probe_opts()
        if self._rt_comm_list:
            self._rt_result.params[self._rt_require.value] = self._rt_comm_list.pop(0)
            return
        raise exception.EnrichCommandException("Strict abstract requirement " + self._rt_require.value +
                                               " is not satisfied")

    def _probe_optional_abstract(self):
        self._probe_opts()
        if self._rt_comm_list:
            self._rt_result.params[self._rt_require.value] = self._rt_comm_list.pop(0)

    def _probe_optional_abstract_list(self):
        while self._rt_comm_list:
            self._probe_opts()
            if self._rt_comm_list:
                if self._rt_require.value not in self._rt_result.params:
                    self._rt_result.params[self._rt_require.value] = []
                self._rt_result.params[self._rt_require.value].append(self._rt_comm_list.pop(0))

    def _probe_opts(self):
        while not self._rt_skip_opts and self._rt_comm_list and \
                self._rt_comm_list.value[0] == '-' and self._rt_comm_list.value != '-':
            if self._rt_comm_list[0].value == '--':
                self._rt_skip_opts = True
                self._rt_comm_list.pop(0)
            else:
                if self._rt_comm_list[0].value.startswith('--'):
                    self._probe_long()
                else:
                    self._probe_short()

    def _probe_long(self):
        node = self._rt_comm_list.pop(0)
        eq_pos = node.value.find('=')
        if eq_pos != -1:
            opt_name = node.value[:eq_pos]
            arg = _CommandScenario._cut_bash_word(node, eq_pos + 1)
        else:
            opt_name = node.value
            arg = None
        opt = self._opt_match(opt_name)

        if opt.arg_required:
            if arg is None:
                if not self._rt_comm_list:
                    exception.EnrichCommandException("Required arg is not provided for opt " + opt.name)
                arg = self._rt_comm_list.pop(0)
        elif arg is not None:
            raise exception.EnrichCommandException("Excessive arg for opt " + opt.name)
        self._rt_opts.append((opt, arg))

    def _probe_short(self):
        node = self._rt_comm_list.pop(0)

        for i in range(1, len(node.value)):
            opt_name = node.value[i]
            opt = self._opt_match("-" + opt_name)
            if opt.arg_required:
                if node.value[i + 1:] != '':
                    arg = _CommandScenario._cut_bash_word(node, i + 1)
                else:
                    if not self._rt_comm_list:
                        raise exception.EnrichCommandException("Required arg is not provided for opt " + opt.name)
                    arg = self._rt_comm_list.pop(0)
                self._rt_opts.append((opt, arg))
                break
            else:
                self._rt_opts.append((opt, None))

    @staticmethod
    def _cut_bash_word(node, start_pos):
        node.value = node.value[start_pos:]
        for child in filter(lambda x: isinstance(x, ast_bash.ParameterNode), node.children):
            if child.pos[0] < start_pos:
                raise exception.EnrichCommandException("Can't cut parameterized word")
            child.pos = child.pos[0] - start_pos, child.pos[1] - start_pos
        return node

    def _opt_match(self, opt_name):
        name_matches = [o for o in self._map_opts if o.startswith(opt_name)]
        if not name_matches:
            raise exception.EnrichCommandException("No matching opts found")
        if opt_name in name_matches:
            return self._map_opts[opt_name]
        if len(name_matches) > 1:
            raise exception.EnrichCommandException("Too many matching opts for " + opt_name)
        return self._map_opts[name_matches[0]]



class BashEnricher(metaclass=MetaSingleton):
    _scenarios = {}

    def __init__(self):
        # TODO
        # init from enrich config
        pass

    @staticmethod
    def _is_allowed(comm):
        return isinstance(comm, ast_bash.CommandNode) and \
               isinstance(comm.children[0], ast_bash.PlainWordNode) and \
               all(isinstance(x, ast_bash.PlainWordNode) or isinstance(x, ast_bash.ParameterizedWordNode) and x.tracked
                   for x in comm.children)

    def enrich_command(self, comm):
        if BashEnricher._is_allowed(comm):
            if isinstance(comm.children[0], ast_bash.PlainWordNode):
                command_name = comm.children[0].value
                for scenario in self._scenarios.get(command_name, []):
                    res = scenario.probe(comm)
                    if res is not None:
                        return res
                globalLog.warning("Suitable scenario not found for command " + comm.line)
