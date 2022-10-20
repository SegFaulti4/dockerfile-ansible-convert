import dockerfile

from src.dockerfile.main import *
from draft_exception import TPDockerfileGeneratorException

from typing import Tuple, Type, Dict


class DockerfileCommandTransformer:

    @staticmethod
    def transform(cmd: dockerfile.Command) -> Tuple[Type, Dict]:
        try:
            res = getattr(DockerfileCommandTransformer, "transform_" + cmd.cmd.lower())(cmd)
            return res
        except AttributeError:
            raise TPDockerfileGeneratorException("Unknown directive " + cmd.cmd)

    @staticmethod
    def transform_run(directive) -> Tuple[Type, Dict]:
        line = " ".join(directive.value)
        return RunDirective, {"line": line}

    @staticmethod
    def transform_env(directive) -> Tuple[Type, Dict]:
        names = directive.value[::2]
        values = directive.value[1::2]
        return EnvDirective, {"names": names, "values": values}

    @staticmethod
    def transform_arg(directive) -> Tuple[Type, Dict]:
        arr = [v.strip('"') for v in directive.value]
        if len(directive.value) == 1:
            arr.append('""')
        return ArgDirective, {"name": arr[0], "value": arr[1]}

    @staticmethod
    def transform_user(directive) -> Tuple[Type, Dict]:
        value = directive.value[0].strip('"')
        name = value[:value.find(':')] if ':' in value else value
        group = value[value.find(':'):] if ':' in value else '""'
        return UserDirective, {"name": name, "group": group}

    @staticmethod
    def transform_workdir(directive) -> Tuple[Type, Dict]:
        path = directive.value[0].strip('"')
        return WorkdirDirective, {"path": path}

    @staticmethod
    def transform_add(directive) -> Tuple[Type, Dict]:
        source, destinations = directive.value[0], directive.value[1:]
        return AddDirective, {"source": source, "destinations": destinations}

    @staticmethod
    def transform_copy(directive) -> Tuple[Type, Dict]:
        source, destinations = directive.value[0], directive.value[1:]
        return CopyDirective, {"source": source, "destinations": destinations}

    @staticmethod
    def transform_from(directive) -> Tuple[Type, Dict]:
        return FromDirective, {"values": directive.value}

    @staticmethod
    def transform_cmd(directive) -> Tuple[Type, Dict]:
        return CmdDirective, {"values": directive.value}

    @staticmethod
    def transform_label(directive) -> Tuple[Type, Dict]:
        return LabelDirective, {"values": directive.value}

    @staticmethod
    def transform_maintainer(directive) -> Tuple[Type, Dict]:
        return MaintainerDirective, {"values": directive.value}

    @staticmethod
    def transform_expose(directive) -> Tuple[Type, Dict]:
        return ExposeDirective, {"values": directive.value}

    @staticmethod
    def transform_entrypoint(directive) -> Tuple[Type, Dict]:
        return EntrypointDirective, {"values": directive.value}

    @staticmethod
    def transform_volume(directive) -> Tuple[Type, Dict]:
        return VolumeDirective, {"values": directive.value}

    @staticmethod
    def transform_onbuild(directive) -> Tuple[Type, Dict]:
        return OnbuildDirective, {"values": directive.value}

    @staticmethod
    def transform_stopsignal(directive) -> Tuple[Type, Dict]:
        return StopsignalDirective, {"values": directive.value}

    @staticmethod
    def transform_healthcheck(directive) -> Tuple[Type, Dict]:
        return HealthcheckDirective, {"values": directive.value}

    @staticmethod
    def transform_shell(directive) -> Tuple[Type, Dict]:
        return ShellDirective, {"values": directive.value}
