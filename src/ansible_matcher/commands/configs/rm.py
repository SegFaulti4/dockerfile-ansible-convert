from src.ansible_matcher.commands.command_config import *


@command_config("rm")
class RmConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("rm <<param : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("force", False, False,
                ['-f', '--force']),

            Opt("interactive once", False, False,
                ['-I']),

            Opt("interactive always", False, False,
                ['-i']),

            Opt("recursive", False, False,
                ['-r', '-R', '--recursive']),

            Opt("directive", False, False,
                ['-d', '--dir']),

            Opt("verbose", False, False,
                ['-v', '--verbose'])
        ]

    @classmethod
    @postprocess_opts("-r")
    def postprocess_r(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-I")
    def postprocess_i(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-i")
    def postprocess_i(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-d")
    def postprocess_d(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-v")
    def postprocess_v(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
