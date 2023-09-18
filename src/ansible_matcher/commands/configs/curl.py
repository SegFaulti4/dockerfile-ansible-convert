from src.ansible_matcher.commands.command_config import *


@command_config("curl")
class CurlConfig(CommandConfigABC):
    entry: ClassVar[TemplateWords] = tmpl_s("curl <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("fail", False, False,
                ['-f', '--fail']),

            Opt("location", False, False,
                ['-L', '--location']),

            Opt("output", True, False,
                ['-o', '--output']),

            Opt("remote name", True, False,
                ['-O', '--remote-name']),

            Opt("show error", False, False,
                ['-S', '--show-error']),

            Opt("silent", False, False,
                ['-s', '--silent'])
        ]

    @classmethod
    @postprocess_opts("-L")
    def postprocess_l(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.uri": {
                "follow_redirects": "safe"
            }
        }

    @classmethod
    @postprocess_opts("-f")
    def postprocess_f(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-S")
    def postprocess_s(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("-s")
    def postprocess_s(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
