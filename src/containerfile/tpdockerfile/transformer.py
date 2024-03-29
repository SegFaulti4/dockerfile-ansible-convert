import dockerfile

from src.containerfile.main import *
from src.exception import TPDockerfileParserException

from typing import Tuple, Type, Dict


class DockerfileCommandTransformer:

    @staticmethod
    def transform(cmd: dockerfile.Command) -> Tuple[Type, Dict]:
        try:
            res = getattr(DockerfileCommandTransformer, "transform_" + cmd.cmd.lower())(cmd)
            return res
        except AttributeError:
            raise TPDockerfileParserException("Unknown directive " + cmd.cmd)

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
        arr = [v for v in directive.value]
        if len(arr) == 1:
            # I hate some people, why would you do that???
            # ARG "var=value"
            if arr[0].startswith('"') and arr[0].endswith('"'):
                arr[0] = arr[0].strip('"')

            if "=" not in arr[0]:
                arr.append('""')
            else:
                pos = arr[0].find('=')
                arr = [arr[0][:pos], arr[0][pos + 1:]]
        return ArgDirective, {"name": arr[0], "value": arr[1]}

    @staticmethod
    def transform_user(directive) -> Tuple[Type, Dict]:
        value = directive.value[0].strip('"')
        name = value[:value.find(':')] if ':' in value else value
        group = value[value.find(':') + 1:] if ':' in value else ""
        return UserDirective, {"name": name, "group": group}

    @staticmethod
    def transform_workdir(directive) -> Tuple[Type, Dict]:
        path = directive.value[0].strip('"')
        return WorkdirDirective, {"path": path}

    @staticmethod
    def transform_add(directive) -> Tuple[Type, Dict]:
        sources, destination = directive.value[:-1], directive.value[-1]
        chown_name, chown_group = "", ""

        for flag in directive.flags:
            if flag.startswith("--chown="):
                value = flag[len("--chown="):].strip('"')
                chown_name = value[:value.find(':')] if ':' in value else value
                chown_group = value[value.find(':') + 1:] if ':' in value else ""

        return AddDirective, {"sources": sources, "destination": destination,
                              "chown_name": chown_name, "chown_group": chown_group}

    @staticmethod
    def transform_copy(directive) -> Tuple[Type, Dict]:
        sources, destination = directive.value[:-1], directive.value[-1]
        chown_name, chown_group = "", ""

        for flag in directive.flags:
            if flag.startswith("--chown="):
                value = flag[len("--chown="):].strip('"')
                chown_name = value[:value.find(':')] if ':' in value else value
                chown_group = value[value.find(':') + 1:] if ':' in value else ""

        return CopyDirective, {"sources": sources, "destination": destination,
                               "chown_name": chown_name, "chown_group": chown_group}

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
