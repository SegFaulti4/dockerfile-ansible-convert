from src.ansible_matcher.commands.command_config import *
from src.ansible_matcher.commands.utils import pip_extra_args


@command_config("pip3 install")
class Pip3InstallConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("pip3 install <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("default timeout", True, False,
                ['--default-timeout', '--timeout']),

            Opt("editable", False, False,
                ['-e', '--editable']),

            Opt("exists action", True, False,
                ['--exists-action']),

            Opt("force-reinstall", False, False,
                ['--force-reinstall']),

            Opt("ignore-installed", False, False,
                ['-I', '--ignore-installed']),

            Opt("index-url", True, False,
                ['-i', '--index-url']),

            Opt("verbose", False, False,
                ['-v', '--verbose']),

            Opt("no-binary", True, True,
                ['--no-binary']),

            Opt("no-cache-dir", False, False,
                ['--no-cache', '--no-cache-dir']),

            Opt("no-index", False, False,
                ['--no-index']),

            Opt("pre", False, False,
                ['--pre']),

            Opt("quiet", False, False,
                ['-q', '--quiet']),

            Opt("requirements", True, False,
                ['-r', '--requirement']),

            Opt("require-hashes", False, False,
                ['--require-hashes']),

            Opt("system", False, False,
                ['--system']),

            Opt("trusted-host", True, False,
                ['--trusted-host']),

            Opt("upgrade", False, False,
                ['-U', '--upgrade']),

            Opt("user", False, False,
                ['--user'])
        ]

    _extra_args = [
        "--default-timeout",
        "--exists-action",
        "--ignore-installed",
        "--index-url",
        "--verbose",
        "--no-binary",
        "--no-cache-dir",
        "--quiet",
        "--pre",
        "--no-index",
        "--trusted-host",
        "--user"
    ]

    @classmethod
    def postprocess_command_opts(cls, call_opts: CommandCallOpts, tweaks: TemplateTweaks) \
            -> Tuple[Dict[str, Any], CommandCallOpts]:

        module_params, unmatched_opts = super().postprocess_command_opts(call_opts, tweaks)
        return pip_extra_args(unmatched_opts=unmatched_opts, opts_name_mapping=cls._opts_name_mapping,
                              opts_alias_mapping=cls._opts_alias_mapping, extra_args=cls._extra_args,
                              module_params=module_params)

    @classmethod
    @postprocess_opts("--editable")
    def postprocess_editable(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "editable": True
            }
        }

    @classmethod
    @postprocess_opts("--force-reinstall")
    def postprocess_forcereinstall(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "state": "forcereinstall"
            }
        }

    @classmethod
    @postprocess_opts("--require-hashes")
    def postprocess_requirehashes(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "aliases": [
                "--require-hashes"
            ],
            "arg_required": False,
            "many_args": False
        }

    @classmethod
    @postprocess_opts("--system")
    def postprocess_system(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "aliases": [
                "--system"
            ],
            "arg_required": False,
            "many_args": False
        }

    @classmethod
    @postprocess_opts("--upgrade")
    def postprocess_upgrade(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "state": "latest"
            }
        }
