from typing import List, Tuple, Type, Dict
from dataclasses import dataclass
from src.shell.main import ShellExpression, ShellScript, ShellParser


class DockerfileDirective:
    pass


@dataclass
class DockerfileContent:
    directives: List[DockerfileDirective]


@dataclass
class RunDirective(DockerfileDirective):
    line: str
    script: ShellScript

    def __len__(self):
        return 5 + len(self.script.line)


@dataclass
class EnvDirective(DockerfileDirective):
    names: List[str]
    values: List[ShellExpression]

    def __len__(self):
        return 4 + sum(1 + len(n) for n in self.names) + sum(1 + len(v.line) for v in self.values)


@dataclass
class ArgDirective(DockerfileDirective):
    name: str
    value: ShellExpression

    def __len__(self):
        return 5 + len(self.name) + len(self.value.line)


@dataclass
class UserDirective(DockerfileDirective):
    name: ShellExpression
    group: ShellExpression

    def __len__(self):
        return 6 + len(self.name.line) + len(self.group.line)


@dataclass
class WorkdirDirective(DockerfileDirective):
    path: ShellExpression

    def __len__(self):
        return 9 + len(self.path.line)


@dataclass
class AddDirective(DockerfileDirective):
    source: ShellExpression
    destinations: List[ShellExpression]

    def __len__(self):
        return 5 + len(self.source.line) + sum(1 + len(d.line) for d in self.destinations)


@dataclass
class CopyDirective(DockerfileDirective):
    source: ShellExpression
    destinations: List[ShellExpression]

    def __len__(self):
        return 6 + len(self.source.line) + sum(1 + len(d.line) for d in self.destinations)


@dataclass
class UnsupportedDirective(DockerfileDirective):
    values: List[str]

    def __len__(self):
        return 1 + sum(1 + len(v) for v in self.values)


@dataclass
class FromDirective(UnsupportedDirective):

    def __len__(self):
        return 4 + super().__len__()


@dataclass
class CmdDirective(UnsupportedDirective):

    def __len__(self):
        return 3 + super().__len__()


@dataclass
class LabelDirective(UnsupportedDirective):

    def __len__(self):
        return 5 + super().__len__()


@dataclass
class MaintainerDirective(UnsupportedDirective):

    def __len__(self):
        return 10 + super().__len__()


@dataclass
class ExposeDirective(UnsupportedDirective):

    def __len__(self):
        return 6 + super().__len__()


@dataclass
class EntrypointDirective(UnsupportedDirective):

    def __len__(self):
        return 10 + super().__len__()


@dataclass
class VolumeDirective(UnsupportedDirective):

    def __len__(self):
        return 6 + super().__len__()


@dataclass
class OnbuildDirective(UnsupportedDirective):

    def __len__(self):
        return 7 + super().__len__()


@dataclass
class StopsignalDirective(UnsupportedDirective):

    def __len__(self):
        return 10 + super().__len__()


@dataclass
class HealthcheckDirective(UnsupportedDirective):

    def __len__(self):
        return 11 + super().__len__()


@dataclass
class ShellDirective(UnsupportedDirective):

    def __len__(self):
        return 5 + super().__len__()


class DockerfileParser:
    shell_parser: ShellParser

    def parse_str(self, val: str) -> List[Tuple[Type, Dict]]:
        raise NotImplementedError

    def from_path(self, path: str) -> DockerfileContent:
        return self.from_stream(open(path, "r"))

    def from_stream(self, file) -> DockerfileContent:
        return self.from_str(file.read())

    def from_str(self, val: str) -> DockerfileContent:
        generate_map = {
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
        directives = [generate_map[t](**a) for t, a in parsed]
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
