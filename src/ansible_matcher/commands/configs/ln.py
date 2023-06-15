from src.ansible_matcher.commands.command_config import *


@command_config("ln")
class LnConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("ln <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("force", False, False,
                ['-f', '--force']),

            Opt("symbolic", False, False,
                ['-s', '--symbolic']),

            Opt("no dereference", False, False,
                ['-n', '--no-dereference']),

            Opt("directory", False, False,
                ['-d', '-F', '--directory']),

            Opt("no target directory", False, False,
                ['-T', '--no-target-directory']),

            Opt("verbose", False, False,
                ['-v', '--verbose'])
        ]

    @classmethod
    @postprocess_opts("--force")
    def postprocess_force(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-dereference")
    def postprocess_nodereference(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.file": {
                "follow": False
            }
        }

    @classmethod
    @postprocess_opts("--verbose")
    def postprocess_verbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
