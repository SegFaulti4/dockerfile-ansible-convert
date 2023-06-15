from src.ansible_matcher.commands.command_config import *


@command_config("mv")
class MvConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("mv <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("force", False, False,
                ['-f', '--force']),

            Opt("verbose", False, False,
                ['--verbose', '-v']),

            Opt("no clobber", False, False,
                ['-n', '--no-clobber']),

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
