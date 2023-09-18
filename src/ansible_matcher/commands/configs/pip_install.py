from src.ansible_matcher.commands.command_config import *
from src.ansible_matcher.commands.utils import pip_extra_args


@command_config("pip install")
class PipInstallConfig(CommandConfigABC):
    entry: ClassVar[TemplateWords] = tmpl_s("pip install <<parameters : m>>")
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

    _extra_args = [
        "--build",
        "--constraint",
        "--cache-dir",
        "--default-timeout",
        "--exists-action",
        "--extra-index-url",
        "--find-links",
        "--index-url",
        "--no-binary",
        "--only-binary",
        "--root",
        "--prefix",
        "--src",
        "--timeout",
        "--trusted-host",
        "--upgrade-strategy",
        "--allow-external",
        "--allow-unverified",
        "--disable-pip-version-check",
        "--ignore-installed",
        "--verbose",
        "--no-cache-dir",
        "--no-clean",
        "--no-deps",
        "--no-input",
        "--no-use-pep517",
        "--no-use-wheel",
        "--pre",
        "--quiet",
        "--require-hashes",
        "--system",
        "--user",
        "--version"
    ]

    @classmethod
    def postprocess_command_opts(cls, cmd_opts: CommandOpts, tweaks: TemplateTweaks) \
            -> Tuple[Dict[str, Any], CommandOpts]:

        module_params, unmatched_opts = super().postprocess_command_opts(cmd_opts, tweaks)
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
    @postprocess_opts("--upgrade")
    def postprocess_upgrade(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.pip": {
                "state": "latest"
            }
        }
