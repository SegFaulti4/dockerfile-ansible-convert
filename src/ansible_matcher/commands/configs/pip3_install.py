from src.ansible_matcher.commands.command_config import *


@command_config("pip3 install")
class Pip3InstallConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("pip3 install <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("default timeout", True, False,
                ['--default-timeout', 'timeout']),

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

    @classmethod
    @postprocess_opts("--default-timeout <<default_timeout_arg>>")
    def postprocess_defaulttimeoutdefaulttimeoutarg(cls, default_timeout_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--default-timeout {default_timeout_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--editable")
    def postprocess_editable(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "editable": True
            }
        }

    @classmethod
    @postprocess_opts("--exists-action <<exists_action_arg>>")
    def postprocess_existsactionexistsactionarg(cls, exists_action_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--exists-action {exists_action_arg} '
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
    @postprocess_opts("--ignore-installed")
    def postprocess_ignoreinstalled(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--ignore-installed "
            }
        }

    @classmethod
    @postprocess_opts("--index-url <<index_url_arg>>")
    def postprocess_indexurlindexurlarg(cls, index_url_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--index-url {index_url_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--verbose")
    def postprocess_verbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--verbose "
            }
        }

    @classmethod
    @postprocess_opts("--no-binary <<no_binary_arg : m>>")
    def postprocess_nobinarynobinaryargm(cls, no_binary_arg: List[str], tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--no-binary={no_binary_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--no-cache-dir")
    def postprocess_nocachedir(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-cache-dir "
            }
        }

    @classmethod
    @postprocess_opts("--no-index")
    def postprocess_noindex(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-index "
            }
        }

    @classmethod
    @postprocess_opts("--pre")
    def postprocess_pre(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--pre "
            }
        }

    @classmethod
    @postprocess_opts("--quiet")
    def postprocess_quiet(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--quiet "
            }
        }

    @classmethod
    @postprocess_opts("require-hashes")
    def postprocess_requirehashes(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "aliases": [
                "--require-hashes"
            ],
            "arg_required": False,
            "many_args": False
        }

    @classmethod
    @postprocess_opts("system")
    def postprocess_system(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "aliases": [
                "--system"
            ],
            "arg_required": False,
            "many_args": False
        }

    @classmethod
    @postprocess_opts("--trusted-host <<trusted_host_arg>>")
    def postprocess_trustedhosttrustedhostarg(cls, trusted_host_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--trusted-host {trusted_host_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--upgrade")
    def postprocess_upgrade(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "state": "latest"
            }
        }

    @classmethod
    @postprocess_opts("--user")
    def postprocess_user(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--user "
            }
        }
