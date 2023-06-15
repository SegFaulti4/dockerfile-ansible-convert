from src.ansible_matcher.commands.command_config import *


@command_config("tar")
class TarConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("tar <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("extract", False, False,
                ['-x', '--extract', '--get']),

            Opt("file", True, False,
                ['-f', '--file']),

            Opt("directory", True, False,
                ['-C', '--directory']),

            Opt("gzip", False, False,
                ['-z', '--gzip']),

            Opt("bzip2", False, False,
                ['-j', '--bzip']),

            Opt("xz", False, False,
                ['-J', '--xz']),

            Opt("absolute names", False, False,
                ['--absolute-names', '-P']),

            Opt("auto compress", False, False,
                ['-a', '--auto-compress']),

            Opt("verbose", False, False,
                ['-v', '--verbose']),

            Opt("create", False, False,
                ['-c', '--create']),

            Opt("exclude", True, False,
                ['--exclude']),

            Opt("no same owner", False, False,
                ['--no-same-owner']),

            Opt("preserve permissions", False, False,
                ['-p', '--preserve-permissions', '--same-permissions']),

            Opt("strip components", True, False,
                ['--strip', '--strip-components'])
        ]

    @classmethod
    @postprocess_opts("-z")
    def postprocess_z(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-j")
    def postprocess_j(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-J")
    def postprocess_j(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--strip-components=<<num>>")
    def postprocess_stripcomponentsnum(cls, num: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.unarchive": {
                "extra_opts": [
                    f'--strip-components={num}'
                ]
            }
        }

    @classmethod
    @postprocess_opts("-v")
    def postprocess_v(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-a")
    def postprocess_a(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-same-owner")
    def postprocess_nosameowner(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.unarchive": {
                "extra_opts": [
                    "--no-same-owner"
                ]
            }
        }

    @classmethod
    @postprocess_opts("--preserve-permissions")
    def postprocess_preservepermissions(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.unarchive": {
                "extra_opts": [
                    "--preserve-permissions"
                ]
            }
        }
