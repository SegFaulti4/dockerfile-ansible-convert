from src.ansible_matcher.commands.command_config import *


@command_config("chmod")
class ChmodConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("chmod <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("changes", False, False,
                ['--changes', '-c']),

            Opt("quiet", False, False,
                ['--quiet', '--silent', '-f']),

            Opt("verbose", False, False,
                ['--verbose', '-v']),

            Opt("no preserve root", False, False,
                ['--no-preserve-root']),

            Opt("preserve root", False, False,
                ['--preserve-root']),

            Opt("reference", True, False,
                ['--reference']),

            Opt("recursive", False, False,
                ['--recursive', '-R']),

            Opt("help", False, False,
                ['--help']),

            Opt("version", False, False,
                ['--version'])
        ]

    @classmethod
    @postprocess_opts("--verbose")
    def postprocess_verbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--changes")
    def postprocess_changes(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--quiet")
    def postprocess_quiet(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
