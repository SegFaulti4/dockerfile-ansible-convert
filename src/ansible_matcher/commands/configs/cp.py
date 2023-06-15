from src.ansible_matcher.commands.command_config import *


@command_config("cp")
class CpConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("cp <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("archive", False, False,
                ['--archive', '-a']),

            Opt("force", False, False,
                ['-f', '--force']),

            Opt("recursive", False, False,
                ['--recursive', '-R', '-r']),

            Opt("verbose", False, False,
                ['--verbose', '-v']),

            Opt("backup", False, False,
                ['--backup']),

            Opt("no dereference reserve links", False, False,
                ['-d']),

            Opt("no clobber", False, False,
                ['-n', '--no-clobber']),

            Opt("preserve mode ownership timestamps", False, False,
                ['-p']),

            Opt("dereference", False, False,
                ['-L', '--dereference']),

            Opt("symbolic", False, False,
                ['-s', '--symbolic-link']),

            Opt("target directory", True, False,
                ['-t', '--target-directory'])
        ]

    @classmethod
    @postprocess_opts("--force")
    def postprocess_force(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--verbose")
    def postprocess_verbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-r")
    def postprocess_r(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--backup")
    def postprocess_backup(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.copy": {
                "backup": True
            }
        }

    @classmethod
    @postprocess_opts("--dereference")
    def postprocess_dereference(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
