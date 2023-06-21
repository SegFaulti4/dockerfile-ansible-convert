from src.ansible_matcher.commands.command_config import *


@command_config("pip uninstall")
class PipUninstallConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("pip uninstall <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("yes", False, False,
                ['-y', '--yes']),

            Opt("no cache dir", False, False,
                ['--no-cache-dir']),

            Opt("requirement", True, False,
                ['-r', '--requirement'])
        ]

    @classmethod
    @postprocess_opts("--yes")
    def postprocess_yes(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-cache-dir")
    def postprocess_nocachedir(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-cache-dir"
            }
        }
