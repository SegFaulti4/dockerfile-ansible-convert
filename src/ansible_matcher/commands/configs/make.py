from src.ansible_matcher.commands.command_config import *


@command_config("make")
class MakeConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("make <<parameters : mo>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("silent", False, False,
                ['-s', '--silent', '--quiet']),

            Opt("jobs", True, False,
                ['-j', '--jobs']),

            Opt("directory", True, False,
                ['-C', '--directory']),

            Opt("file", True, False,
                ['-f', '--file', '--makefile'])
        ]

    @classmethod
    @postprocess_opts("-C <<directory : p>>")
    def postprocess_cdirp(cls, directory: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "community.general.make": {
                "chdir": directory
            }
        }

    @classmethod
    @postprocess_opts("-j <<n_jobs>>")
    def postprocess_jnjobs(cls, n_jobs: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "community.general.make": {
                "jobs": n_jobs
            }
        }

    @classmethod
    @postprocess_opts("-f <<file : p>>")
    def postprocess_ffilep(cls, file: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "community.general.make": {
                "file": file
            }
        }

    @classmethod
    @postprocess_opts("-s")
    def postprocess_s(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
