from src.ansible_matcher.commands.command_config import *


@command_config("git clone")
class GitCloneConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("git clone <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("branch", True, False,
                ['-b', '--branch']),

            Opt("depth", True, False,
                ['--depth']),

            Opt("recurse submodules", False, False,
                ['--recurse-submodule', '--recursive']),

            Opt("quiet", False, False,
                ['-q', '--quiet'])
        ]

    @classmethod
    @postprocess_opts("--quiet")
    def postprocess_quiet(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--recurse-submodule")
    def postprocess_recursesubmodule(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.git": {
                "recursive": True
            }
        }

    @classmethod
    @postprocess_opts("--depth <<depth>>")
    def postprocess_depthdepth(cls, depth: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.git": {
                "depth": depth
            }
        }

    @classmethod
    @postprocess_opts("--branch <<branch>>")
    def postprocess_branchbranch(cls, branch: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.git": {
                "version": branch
            }
        }
