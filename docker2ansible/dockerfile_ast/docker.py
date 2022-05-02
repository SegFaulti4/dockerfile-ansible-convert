from typing import List

from docker2ansible.dockerfile_ast.bash import parse_bash, parse_bash_value
import docker2ansible.dockerfile_ast.ast as ast
from dataclasses import dataclass, field


@dataclass
class Node(ast.Node):

    def _process(self):
        raise NotImplementedError


@dataclass
class UnusedNode(ast.Node):

    value: List = field(default_factory=list)

    def __init__(self, directive):
        self.value.extend(directive.value)

    def _process(self):
        pass


@dataclass
class FromNode(Node):

    image_name: str = ""
    repo: str = ""
    tag: str = ""

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

    line: str = ""

    def __init__(self, directive):
        self.line = directive.value[0]
        self.children = parse_bash(self.line)

    def _process(self):
        # TODO
        pass


@dataclass
class EnvNode(Node):

    names: List = field(default_factory=list)
    values: List = field(default_factory=list)

    def __init__(self, directive):
        self.names.extend(directive.value[::2])
        self.values.extend(directive.value[1::2])
        self.children = [parse_bash_value(value) for value in self.values]

    def _process(self):
        # TODO
        pass


@dataclass
class AddNode(Node):

    sources: List = field(default_factory=list)
    dst: str = ""

    def __init__(self, directive):
        self.dst = directive.value[0]
        self.sources.extend(directive.value[1:])
        self.children = [parse_bash_value(self.dst)] + \
                        [parse_bash_value(value) for value in self.sources]

    def _process(self):
        # TODO
        pass


@dataclass
class CopyNode(Node):

    sources: List = field(default_factory=list)
    dst: str = ""

    def __init__(self, directive):
        self.dst = directive.value[0]
        self.sources.extend(directive.value[1:])
        self.children = [parse_bash_value(self.dst)] + \
                        [parse_bash_value(value) for value in self.sources]

    def _process(self):
        # TODO
        pass


@dataclass
class ArgNode(Node):

    name: str = ""
    value: str = ""

    def __init__(self, directive):
        self.name = directive.value[0] \
            if '=' not in directive.value[0] \
            else directive.value[0].split('=')[0].strip()
        self.value = directive.value[0].split('=')[-1].strip() \
            if '=' in directive.value[0] \
            else None

    def _process(self):
        # TODO
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
