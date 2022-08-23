from typing import List, Tuple, Type, Dict
from dataclasses import dataclass
from lib.shell.main import ShellExpression, ShellScript, ShellParser


class DockerfileDirective:
    pass


class DockerfileContent:
    directives: List[DockerfileDirective]


@dataclass
class RunDirective(DockerfileDirective):
    line: str
    script: ShellScript


@dataclass
class EnvDirective(DockerfileDirective):
    names: List[str]
    values: List[ShellExpression]


@dataclass
class ArgDirective(DockerfileDirective):
    name: str
    value: ShellExpression


@dataclass
class UserDirective(DockerfileDirective):
    name: ShellExpression
    group: ShellExpression


@dataclass
class WorkdirDirective(DockerfileDirective):
    path: ShellExpression


@dataclass
class AddDirective(DockerfileDirective):
    source: ShellExpression
    destinations: List[ShellExpression]


@dataclass
class CopyDirective(DockerfileDirective):
    source: ShellExpression
    destinations: List[ShellExpression]


@dataclass
class UselessDirective(DockerfileDirective):
    values: List[str]


@dataclass
class FromDirective(UselessDirective):
    pass


@dataclass
class CmdDirective(UselessDirective):
    pass


@dataclass
class LabelDirective(UselessDirective):
    pass


@dataclass
class MaintainerDirective(UselessDirective):
    pass


@dataclass
class ExposeDirective(UselessDirective):
    pass


@dataclass
class EntrypointDirective(UselessDirective):
    pass


@dataclass
class VolumeDirective(UselessDirective):
    pass


@dataclass
class OnbuildDirective(UselessDirective):
    pass


@dataclass
class StopsignalDirective(UselessDirective):
    pass


@dataclass
class HealthcheckDirective(UselessDirective):
    pass


@dataclass
class ShellDirective(UselessDirective):
    pass


class DockerfileContentGenerator:
    shell_parser: ShellParser

    def parse_str(self, val: str) -> List[Tuple[Type, Dict]]:
        raise NotImplementedError

    def from_path(self, path: str) -> DockerfileContent:
        return self.from_stream(open(path, "w"))

    def from_stream(self, file) -> DockerfileContent:
        return self.from_str(file.read())

    def from_str(self, val: str) -> DockerfileContent:
        generate_type_map = {
            RunDirective: self._generate_run,
            EnvDirective: self._generate_env,
            ArgDirective: self._generate_arg,
            UserDirective: self._generate_user,
            WorkdirDirective: self._generate_workdir,
            AddDirective: self._generate_add,
            CopyDirective: self._generate_copy,
            FromDirective: self._generate_from,
            CmdDirective: self._generate_cmd,
            LabelDirective: self._generate_label,
            MaintainerDirective:  self._generate_maintainer,
            ExposeDirective: self._generate_expose,
            EntrypointDirective: self._generate_entrypoint,
            VolumeDirective: self._generate_volume,
            OnbuildDirective: self._generate_onbuild,
            StopsignalDirective: self._generate_stopsignal,
            HealthcheckDirective: self._generate_healthcheck,
            ShellDirective: self._generate_shell
        }
        parsed = self.parse_str(val)
        directives = [generate_type_map[t](*a) for t, a in parsed]
        return DockerfileContent(directives=directives)

    def _generate_run(self, line: str) -> RunDirective:
        script = self.shell_parser.parse_as_script(line)
        return RunDirective(line=line, script=script)

    def _generate_env(self, names: List[str], values: List[str]) -> EnvDirective:
        expressions = [self.shell_parser.parse_as_expression(val) for val in values]
        return EnvDirective(names=names, values=expressions)

    def _generate_arg(self, name: str, value: str) -> ArgDirective:
        expression = self.shell_parser.parse_as_expression(value)
        return ArgDirective(name=name, value=expression)

    def _generate_user(self, name: str, group: str) -> UserDirective:
        name_expr = self.shell_parser.parse_as_expression(name)
        group_expr = self.shell_parser.parse_as_expression(group)
        return UserDirective(name=name_expr, group=group_expr)

    def _generate_workdir(self, path: str) -> WorkdirDirective:
        path_expr = self.shell_parser.parse_as_expression(path)
        return WorkdirDirective(path=path_expr)

    def _generate_add(self, source: str, destinations: List[str]) -> AddDirective:
        source_expr = self.shell_parser.parse_as_expression(source)
        destinations_expr = [self.shell_parser.parse_as_expression(dest) for dest in destinations]
        return AddDirective(source=source_expr, destinations=destinations_expr)

    def _generate_copy(self, source: str, destinations: List[str]) -> CopyDirective:
        source_expr = self.shell_parser.parse_as_expression(source)
        destinations_expr = [self.shell_parser.parse_as_expression(dest) for dest in destinations]
        return CopyDirective(source=source_expr, destinations=destinations_expr)

    def _generate_from(self, values: List[str]) -> FromDirective:
        return FromDirective(values=values)

    def _generate_cmd(self, values: List[str]) -> CmdDirective:
        return CmdDirective(values=values)

    def _generate_label(self, values: List[str]) -> LabelDirective:
        return LabelDirective(values=values)

    def _generate_maintainer(self, values: List[str]) -> MaintainerDirective:
        return MaintainerDirective(values=values)

    def _generate_expose(self, values: List[str]) -> ExposeDirective:
        return ExposeDirective(values=values)

    def _generate_entrypoint(self, values: List[str]) -> EntrypointDirective:
        return EntrypointDirective(values=values)

    def _generate_volume(self, values: List[str]) -> VolumeDirective:
        return VolumeDirective(values=values)

    def _generate_onbuild(self, values: List[str]) -> OnbuildDirective:
        return OnbuildDirective(values=values)

    def _generate_stopsignal(self, values: List[str]) -> StopsignalDirective:
        return StopsignalDirective(values=values)

    def _generate_healthcheck(self, values: List[str]) -> HealthcheckDirective:
        return HealthcheckDirective(values=values)

    def _generate_shell(self, values: List[str]) -> ShellDirective:
        return ShellDirective(values=values)
