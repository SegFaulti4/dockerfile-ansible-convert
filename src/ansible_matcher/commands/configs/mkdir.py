from src.ansible_matcher.commands.command_config import *


@command_config("mkdir")
class MkdirConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("mkdir <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("mode", False, False,
                ['-m', '--mode']),

            Opt("parents", False, False,
                ['-p', '--parents']),

            Opt("verbose", False, False,
                ['-v', '--verbose'])
        ]

    @classmethod
    @postprocess_opts("-m <<mode>>")
    def postprocess_mmode(cls, mode: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.file": {
                "mode": mode
            }
        }

    @classmethod
    @postprocess_opts("-v")
    def postprocess_v(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
