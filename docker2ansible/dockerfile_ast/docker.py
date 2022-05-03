from typing import List

import docker2ansible.dockerfile_ast.bash as ast_bash
import docker2ansible.dockerfile_ast.ast as ast
from dataclasses import dataclass, field


@dataclass
class Node(ast.Node):

    def _process(self):
        raise NotImplementedError


@dataclass
class UnusedNode(ast.Node):

    value = []

    def __init__(self, directive):
        self.value.extend(directive.value)

    def _process(self):
        pass


@dataclass
class FromNode(Node):

    image_name = None
    repo = None
    tag = None

    def __init__(self, directive):
        value = directive.value[0]
        name = value.split('/')[-1].strip() if '/' in value else value
        name = name.split(':')[0].strip() if ':' in name else name

        self.image_name = name

        if '/' in value:
            self.repo = value.split('/')[0].strip()

        if ':' in value:
            self.tag = value.split(':')[-1].strip()

    def _process(self):
        pass


@dataclass
class RunNode(Node):

    line = None

    def __init__(self, directive):
        self.stack.setup_local_stack()
        self.line = directive.value[0]
        self.children = ast_bash.parse_bash(self.line)

    def _process(self):
        # TODO
        # enrich command
        pass


@dataclass
class EnvNode(Node):

    names = []
    values = []

    def __init__(self, directive):
        self.names.extend(directive.value[::2])
        self.values.extend(directive.value[1::2])
        self.children = [ast_bash.parse_bash_value(value) for value in self.values]
        for i in range(len(self.values)):
            self.stack.add_global_var(self.names[i], self.values[i])

    def _process(self):
        pass


@dataclass
class AddNode(Node):

    sources = []
    dst = None

    def __init__(self, directive):
        self.dst = directive.value[0]
        self.sources.extend(directive.value[1:])
        self.children = [ast_bash.parse_bash_value(self.dst)] + \
                        [ast_bash.parse_bash_value(value) for value in self.sources]

    def _process(self):
        pass


@dataclass
class CopyNode(Node):

    sources = []
    dst = None

    def __init__(self, directive):
        self.dst = directive.value[0]
        self.sources.extend(directive.value[1:])
        self.children = [ast_bash.parse_bash_value(self.dst)] + \
                        [ast_bash.parse_bash_value(value) for value in self.sources]

    def _process(self):
        pass


@dataclass
class ArgNode(Node):

    name = None
    value = None

    def __init__(self, directive):
        self.name = directive.value[0] \
            if '=' not in directive.value[0] \
            else directive.value[0].split('=')[0].strip()
        self.value = directive.value[0].split('=')[-1].strip() \
            if '=' in directive.value[0] \
            else None

    def _process(self):
        pass


@dataclass
class CmdNode(UnusedNode):
    pass


@dataclass
class LabelNode(UnusedNode):
    pass


@dataclass
class MaintainerNode(UnusedNode):
    pass


@dataclass
class ExposeNode(UnusedNode):
    pass


@dataclass
class EntrypointNode(UnusedNode):
    pass


@dataclass
class VolumeNode(UnusedNode):
    pass


@dataclass
class UserNode(UnusedNode):
    pass


@dataclass
class WorkdirNode(UnusedNode):
    pass


@dataclass
class OnbuildNode(UnusedNode):
    pass


@dataclass
class StopsignalNode(UnusedNode):
    pass


@dataclass
class HealthcheckNode(UnusedNode):
    pass


@dataclass
class ShellNode(UnusedNode):
    pass
