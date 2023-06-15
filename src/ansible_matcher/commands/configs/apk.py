from src.ansible_matcher.commands.command_config import *


@command_config("apk")
class ApkConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("apk <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("force", False, False,
                ['-f', '--force']),

            Opt("interactive", False, False,
                ['-i', '--interactive']),

            Opt("root", True, False,
                ['-p', '--root']),

            Opt("quiet", False, False,
                ['-q', '--quiet']),

            Opt("update-cache", False, False,
                ['-U', '--update-cache']),

            Opt("verbose", False, False,
                ['-v', '--verbose']),

            Opt("repository", True, False,
                ['-X', '--repository']),

            Opt("allow-untrusted", False, False,
                ['--allow-untrusted']),

            Opt("architecture", True, False,
                ['--arch']),

            Opt("cache-dir", True, False,
                ['--cache-dir']),

            Opt("cache-max-age", True, False,
                ['--cache-max-age']),

            Opt("force-binary-stdout", False, False,
                ['--force-binary-stdout']),

            Opt("force-broken-world", False, False,
                ['--force-broken-world']),

            Opt("force-non-repository", False, False,
                ['--force-non-repository']),

            Opt("force-old-apk", False, False,
                ['--force-old-apk']),

            Opt("force-overwrite", False, False,
                ['--force-overwrite']),

            Opt("force-refresh", False, False,
                ['--force-refresh']),

            Opt("keys-dir", True, False,
                ['--keys-dir']),

            Opt("no-cache", False, False,
                ['--no-cache']),

            Opt("no-network", False, False,
                ['--no-network']),

            Opt("no-progress", False, False,
                ['--no-progress']),

            Opt("print-arch", False, False,
                ['--print-arch']),

            Opt("progress", False, False,
                ['--progress']),

            Opt("progress-fd", True, False,
                ['--progress-fd']),

            Opt("purge", False, False,
                ['--purge']),

            Opt("repositories-file", True, False,
                ['--repositories-file']),

            Opt("wait", True, False,
                ['--wait'])
        ]

    @classmethod
    @postprocess_opts("--interactive")
    def postprocess_interactive(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--quiet")
    def postprocess_quiet(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--verbose")
    def postprocess_verbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-progress")
    def postprocess_noprogress(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--progress")
    def postprocess_progress(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--progress-fd <<value>>")
    def postprocess_progressfd(cls, value: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
