import json
import dockerfile
from dataclasses import dataclass

import docker2ansible.dockerfile_ast.docker as ast_docker
import docker2ansible.dockerfile_ast.bash as ast_bash
from docker2ansible.dockerfile_ast._meta import _MetaSingleton


def create_dockerfile_ast(filepath):
    parsed = dockerfile.parse_file(filepath.strip())
    ast = {'type': 'DOCKER-FILE', 'children': [], 'meta_info': filepath}

    for directive in parsed:
        cmd = str(directive.cmd).lower()
        cmd = cmd[0:1].upper() + cmd[1:]
        ast['children'].append(getattr(ast_docker, cmd + 'Node')(directive))


class Stack(metaclass=_MetaSingleton):

    _dockerfile_level = dict()
    _directive_level = dict()

    def add_global_var(self, name, value):
        self._dockerfile_level[name] = value
        self._resolve_var(name)

    def add_local_var(self, name, value):
        self._directive_level[name] = value
        self._resolve_var(name)

    def setup_local_stack(self):
        self._directive_level.clear()

    def contains(self, name):
        return self._get(name) is not None

    def _get(self, name):
        res = self._directive_level.get(name, None)
        if res is not None:
            return res
        return self._dockerfile_level.get(name, None)

    def resolvable(self, name):
        value = self._get(name)
        if value is not None:
            return isinstance(value, ast_bash.ConstantValueNode) or \
                   isinstance(value, ast_bash.ParameterizedValueNode) and value.resolvable
        return False

    def _resolve_var(self, name):
        # TODO
        pass

    def resolve_var(self, name):
        # TODO
        pass

    def resolve_command(self, comm):
        # TODO
        pass


@dataclass
class Node:

    stack = Stack()
    children = []

    # def __init__(**kwargs):
    #     assert any(map(lambda x: not isinstance(x, Node), kwargs.get('children', [])))
    #     self.__dict__.update(kwargs)

    def __post_init__(self):
        self._process()

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=True)

    def _process(self):
        raise NotImplementedError

    # def _visit(self):
    #     self._process()
    #     child: Node
    #     for child in self.children:
    #        child._visit()
