from enum import Enum
from dataclasses import dataclass

import docker2ansible.dockerfile_ast.enrich_config as enrich_config
import docker2ansible.dockerfile_ast.bash as ast_bash
from docker2ansible.dockerfile_ast._meta import _MetaSingleton
from docker2ansible import exception
from docker2ansible.log import globalLog


@dataclass
class _CommandParameter:
    class Type(Enum):
        CONSTANT = 1
        SINGLE_ABSTRACT = 2
        ABSTRACT_LIST = 3

    type: Type
    value: str


class _CommandScenario:
    command_name = None
    _requires = []
    _options = []
    _options_map = {}

    def __init__(self, config):
        # TODO
        # init from enrich config
        pass

    def probe(self, comm):
        # TODO
        pass


class BashEnricher(metaclass=_MetaSingleton):
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
