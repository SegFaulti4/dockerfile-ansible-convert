from src.ansible_matcher.commands.command_config import *


@command_config("pip install")
class PipInstallConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("pip install <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("build", True, False,
                ['--build']),

            Opt("constraint", True, False,
                ['-c', '--constraint']),

            Opt("cache-dir", True, False,
                ['--cache-dir']),

            Opt("default-timeout", True, False,
                ['--default-timeout']),

            Opt("exists-action", True, False,
                ['--exists-action']),

            Opt("extra-index-url", True, False,
                ['--extra-index-url']),

            Opt("find-links", True, False,
                ['-f', '--find-links']),

            Opt("index-url", True, False,
                ['-i', '--index-url']),

            Opt("install-option", True, True,
                ['--install-option']),

            Opt("no-binary", True, False,
                ['--no-binary']),

            Opt("only-binary", True, False,
                ['--only-binary']),

            Opt("requirement", True, False,
                ['-r', '--requirement']),

            Opt("root", True, False,
                ['--root']),

            Opt("prefix", True, False,
                ['--prefix']),

            Opt("src", True, False,
                ['--src']),

            Opt("timeout", True, False,
                ['--timeout']),

            Opt("trusted-host", True, False,
                ['--trusted-host']),

            Opt("upgrade-strategy", True, False,
                ['--upgrade-strategy']),

            Opt("allow-external", False, False,
                ['--allow-external']),

            Opt("allow-unverified", False, False,
                ['--allow-unverified']),

            Opt("disable-pip-version-check", False, False,
                ['--disable-pip-version-check']),

            Opt("editable", False, False,
                ['-e', '--editable']),

            Opt("force-reinstall", False, False,
                ['--force-reinstall']),

            Opt("ignore-installed", False, False,
                ['-I', '--ignore-installed']),

            Opt("upgrade", False, False,
                ['-U', '--upgrade']),

            Opt("verbose", False, False,
                ['-v', '--verbose']),

            Opt("no-cache-dir", False, False,
                ['--no-cache', '--no-cache-dir']),

            Opt("no-clean", False, False,
                ['--no-clean']),

            Opt("no-dependencies", False, False,
                ['--no-dependencies', '--no-deps']),

            Opt("no-input", False, False,
                ['--no-input']),

            Opt("no-use-pep517", False, False,
                ['--no-use-pep517']),

            Opt("no-use-wheel", False, False,
                ['--no-use-wheel']),

            Opt("pre", False, False,
                ['--pre']),

            Opt("quiet", False, False,
                ['-q', '--quiet']),

            Opt("require-hashes", False, False,
                ['--require-hashes']),

            Opt("system", False, False,
                ['--system']),

            Opt("user", False, False,
                ['--user']),

            Opt("version", False, False,
                ['--version'])
        ]

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
    @postprocess_opts("--upgrade")
    def postprocess_upgrade(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "state": "latest"
            }
        }

    @classmethod
    @postprocess_opts("--build <<build_arg>>")
    def postprocess_buildbuildarg(cls, build_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--build {build_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--constraint <<constraint_arg>>")
    def postprocess_constraintconstraintarg(cls, constraint_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--constraint {constraint_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--cache-dir <<cache_dir_arg>>")
    def postprocess_cachedircachedirarg(cls, cache_dir_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--cache-dir {cache_dir_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--default-timeout <<default_timeout_arg>>")
    def postprocess_defaulttimeoutdefaulttimeoutarg(cls, default_timeout_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--default-timeout {default_timeout_arg} '
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
    @postprocess_opts("--extra-index-url <<extra_index_url_arg>>")
    def postprocess_extraindexurlextraindexurlarg(cls, extra_index_url_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--extra-index-url {extra_index_url_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--find-links <<find_links_arg>>")
    def postprocess_findlinksfindlinksarg(cls, find_links_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--find-links {find_links_arg} '
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
    @postprocess_opts("--no-binary <<no_binary_arg : m>>")
    def postprocess_nobinarynobinaryargm(cls, no_binary_arg: List[str], tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--no-binary={no_binary_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--only-binary <<only_binary_arg>>")
    def postprocess_onlybinaryonlybinaryarg(cls, only_binary_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--only-binary {only_binary_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--root <<root_arg>>")
    def postprocess_rootrootarg(cls, root_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--root {root_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--prefix <<prefix_arg>>")
    def postprocess_prefixprefixarg(cls, prefix_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--prefix {prefix_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--src <<src_arg>>")
    def postprocess_srcsrcarg(cls, src_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--src {src_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--timeout <<timeout_arg>>")
    def postprocess_timeouttimeoutarg(cls, timeout_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--timeout {timeout_arg} '
            }
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
    @postprocess_opts("--upgrade-strategy <<upgrade_strategy_arg>>")
    def postprocess_upgradestrategyupgradestrategyarg(cls, upgrade_strategy_arg: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": f'--upgrade-strategy {upgrade_strategy_arg} '
            }
        }

    @classmethod
    @postprocess_opts("--allow-external")
    def postprocess_allowexternal(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--allow-external "
            }
        }

    @classmethod
    @postprocess_opts("--allow-unverified")
    def postprocess_allowunverified(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--allow-unverified "
            }
        }

    @classmethod
    @postprocess_opts("--disable-pip-version-check")
    def postprocess_disablepipversioncheck(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--disable-pip-version-check "
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
    @postprocess_opts("--verbose")
    def postprocess_verbose(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--verbose "
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
    @postprocess_opts("--no-clean")
    def postprocess_noclean(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-clean "
            }
        }

    @classmethod
    @postprocess_opts("--no-deps")
    def postprocess_nodeps(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-deps "
            }
        }

    @classmethod
    @postprocess_opts("--no-input")
    def postprocess_noinput(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-input "
            }
        }

    @classmethod
    @postprocess_opts("--no-use-pep517")
    def postprocess_nousepep(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-use-pep517 "
            }
        }

    @classmethod
    @postprocess_opts("--no-use-wheel")
    def postprocess_nousewheel(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--no-use-wheel "
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
    @postprocess_opts("--require-hashes")
    def postprocess_requirehashes(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--require-hashes "
            }
        }

    @classmethod
    @postprocess_opts("--system")
    def postprocess_system(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--system "
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

    @classmethod
    @postprocess_opts("--version")
    def postprocess_version(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "extra_args": "--version "
            }
        }
