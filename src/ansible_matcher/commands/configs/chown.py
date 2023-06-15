from src.ansible_matcher.commands.command_config import *


@command_config("chown")
class ChownConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("chown <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("quiet", False, False,
                ['--quiet', '--silent', '-f']),

            Opt("recursive", False, False,
                ['--recursive', '-R']),

            Opt("no dereference", False, False,
                ['-h', '--no-dereference']),

            Opt("verbose", False, False,
                ['--verbose', '-v'])
        ]

    @classmethod
    @postprocess_opts("--quiet")
    def postprocess_quiet(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--verbose")
    def postprocess_verbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-dereference")
    def postprocess_nodereference(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.file": {
                "follow": False
            }
        }
