from src.ansible_matcher.commands.command_config import *


@command_config("wget")
class WgetConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("wget <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("output document", True, False,
                ['-O', '--output-document']),

            Opt("output file", True, False,
                ['-o', '--output-file']),

            Opt("no check certificate", False, False,
                ['--no-check-certificate']),

            Opt("no clobber", False, False,
                ['-nc', '--no-clobber']),

            Opt("header", True, False,
                ['--header']),

            Opt("relative", False, False,
                ['-L', '--relative']),

            Opt("prefix", True, False,
                ['-P', '--directory-prefix']),

            Opt("continue", False, False,
                ['-c', '--continue']),

            Opt("recursive", False, False,
                ['-r', '--recursive']),

            Opt("no parent", False, False,
                ['-np', '--no-parent']),

            Opt("no cookies", False, False,
                ['--no-cookies']),

            Opt("span hosts", False, False,
                ['-H', '--span-hosts']),

            Opt("cur dirs", True, False,
                ['--cur-dirs']),

            Opt("local encoding", True, False,
                ['--local-encoding']),

            Opt("timestamping", False, False,
                ['-N', '--timestamping']),

            Opt("content disposition", False, False,
                ['--content-disposition']),

            Opt("accept", False, False,
                ['-A', '--accept']),

            Opt("tries", False, False,
                ['-t', '--tries']),

            Opt("progress", True, False,
                ['--progress']),

            Opt("no verbose", False, False,
                ['-nv', '--no-verbose']),

            Opt("quiet", False, False,
                ['-q', '--quiet']),

            Opt("help", False, False,
                ['-h', '--help']),

            Opt("version", False, False,
                ['-v', '--version'])
        ]

    @classmethod
    @postprocess_opts("-O <<file : p>>")
    def postprocess_ofilep(cls, file: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.get_url": {
                "dest": file
            }
        }

    @classmethod
    @postprocess_opts("--no-check-certificate")
    def postprocess_nocheckcertificate(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.get_url": {
                "validate_certs": False
            }
        }

    @classmethod
    @postprocess_opts("--no-clobber")
    def postprocess_noclobber(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.get_url": {
                "force": False
            }
        }

    @classmethod
    @postprocess_opts("-P <<file : p>>")
    def postprocess_pfilep(cls, file: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.get_url": {
                "dest": file
            }
        }

    @classmethod
    @postprocess_opts("--progress <<type>>")
    def postprocess_progresstype(cls, type: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-verbose")
    def postprocess_noverbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--quiet")
    def postprocess_quiet(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
