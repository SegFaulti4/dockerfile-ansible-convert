import json
from typing import List

import dockerfile
from dataclasses import dataclass, field
import docker2ansible.dockerfile_ast.docker


def create_dockerfile_ast(filepath):
    parsed = dockerfile.parse_file(filepath.strip())
    ast = {'type': 'DOCKER-FILE', 'children': [], 'meta_info': filepath}

    for directive in parsed:
        cmd = str(directive.cmd).lower()
        cmd = cmd[0:1].upper() + cmd[1:]
        ast['children'].append(getattr(docker2ansible.dockerfile_ast.docker, cmd + 'Node')(directive))


@dataclass
class Node:

    children: List = field(default_factory=list)

    # def __init__(**kwargs):
    #     assert any(map(lambda x: not isinstance(x, Node), kwargs.get('children', [])))
    #     self.__dict__.update(kwargs)

    def __post_init__(self):
        self._process()

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=True)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__)))

    def _process(self):
        raise NotImplementedError

    def _visit(self):
        self._process()
        child: Node
        for child in self.children:
            child._visit()
