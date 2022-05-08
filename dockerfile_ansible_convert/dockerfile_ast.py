import json
from dataclasses import dataclass
from typing import List
import dockerfile

import dockerfile_ansible_convert.bash_parse as bash_parse
import exception as exception
from log import globalLog


def create_from_path(path):
    try:
        parsed = dockerfile.parse_file(path.strip())

        nodes = []
        for directive in parsed:
            nodes.extend(DirectiveTransformer.transform(directive))

        return AST(meta_info=path, directives=nodes)
    except Exception as exc:
        globalLog.error(type(exc))
        globalLog.error(exc)
        globalLog.error("Failed to create dockerfile AST")
        return None


class NodeEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


@dataclass(repr=False)
class Node:
    children: List

    def __repr__(self):
        return json.dumps(self, indent=4, sort_keys=True, cls=NodeEncoder)


@dataclass(repr=False)
class DefaultNode(Node):
    values: List


@dataclass(repr=False)
class AST:
    directives: List[Node]
    meta_info: str

    def __repr__(self):
        return json.dumps(self, indent=4, sort_keys=True, cls=NodeEncoder)


class DirectiveTransformer:

    @staticmethod
    def transform(directive):
        try:
            res = getattr(DirectiveTransformer, "_transform_" + directive.cmd.lower())(directive)
            return res
        except AttributeError:
            raise exception.DockerfileASTException("Unknown directive " + directive.cmd)

    @staticmethod
    def _transform_from(directive):
        value = directive.value[0]
        name = value.split('/')[-1].strip() if '/' in value else value
        name = name.split(':')[0].strip() if ':' in name else name

        repo = value.split('/')[0].strip() if '/' in value else ''
        tag = value.split(':')[-1].strip() if ':' in value else ''

        return [FromNode(children=[], image_name=name, repo=repo, tag=tag)]

    @staticmethod
    def _transform_run(directive):
        line = directive.value[0]
        commands = bash_parse.parse_bash_commands(line)

        return [RunNode(children=commands, line=line)]

    @staticmethod
    def _transform_env(directive):
        names = directive.value[::2]
        values = directive.value[1::2]
        children = [bash_parse.parse_bash_value(v) for v in values]

        return [EnvNode(name=name, children=[child]) for name, child in zip(names, children)]

    @staticmethod
    def _transform_add(directive):
        children = [bash_parse.parse_bash_value(v) for v in directive.value]

        return [AddNode(children=children)]

    @staticmethod
    def _transform_copy(directive):
        children = [bash_parse.parse_bash_value(v) for v in directive.value]

        return [CopyNode(children=children)]

    @staticmethod
    def _transform_arg(directive):
        name = directive.value[0] \
            if '=' not in directive.value[0] \
            else directive.value[0].split('=')[0].strip()
        value = directive.value[0].split('=')[-1].strip() \
            if '=' in directive.value[0] \
            else ""

        return [ArgNode(children=[], name=name, value=value)]

    @staticmethod
    def _transform_cmd(directive):
        return [CmdNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_label(directive):
        return [LabelNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_maintainer(directive):
        return [MaintainerNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_expose(directive):
        return [ExposeNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_entrypoint(directive):
        return [EntrypointNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_volume(directive):
        return [VolumeNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_user(directive):
        return [UserNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_workdir(directive):
        return [WorkdirNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_onbuild(directive):
        return [OnbuildNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_stopsignal(directive):
        return [StopsignalNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_healthcheck(directive):
        return [HealthcheckNode(children=[], values=directive.value)]

    @staticmethod
    def _transform_shell(directive):
        return [ShellNode(children=[], values=directive.value)]


@dataclass(repr=False)
class FromNode(Node):
    image_name: str
    repo: str
    tag: str


@dataclass(repr=False)
class RunNode(Node):
    line: str


@dataclass(repr=False)
class EnvNode(Node):
    name: str


class AddNode(Node):
    pass


class CopyNode(Node):
    pass


@dataclass(repr=False)
class ArgNode(Node):
    name: str
    value: str


class CmdNode(DefaultNode):
    pass


class LabelNode(DefaultNode):
    pass


class MaintainerNode(DefaultNode):
    pass


class ExposeNode(DefaultNode):
    pass


class EntrypointNode(DefaultNode):
    pass


class VolumeNode(DefaultNode):
    pass


class UserNode(DefaultNode):
    pass


class WorkdirNode(DefaultNode):
    pass


class OnbuildNode(DefaultNode):
    pass


class StopsignalNode(DefaultNode):
    pass


class HealthcheckNode(DefaultNode):
    pass


class ShellNode(DefaultNode):
    pass
