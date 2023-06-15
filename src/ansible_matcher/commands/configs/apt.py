from src.ansible_matcher.commands.command_config import *


@command_config("apt")
class AptConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("apt-get <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("allow-change-held-packages", False, False,
                ['--allow-change-held-packages']),

            Opt("allow-downgrades", False, False,
                ['--allow-downgrades']),

            Opt("allow-releaseinfo-change", False, False,
                ['--allow-releaseinfo-change']),

            Opt("allow-remove-essential", False, False,
                ['--allow-remove-essential']),

            Opt("allow-unauthenticated", False, False,
                ['--allow-unauthenticated']),

            Opt("arch-only", False, False,
                ['--arch-only']),

            Opt("assume-no", False, False,
                ['--assume-no']),

            Opt("assume-yes", False, False,
                ['-y', '--yes', '--assume-yes']),

            Opt("autoremove", False, False,
                ['--auto-remove', '--autoremove']),

            Opt("build", False, False,
                ['-b', '--compile', '--build']),

            Opt("build-profiles", True, False,
                ['-P', '--build-profiles']),

            Opt("config-file", True, False,
                ['-c', '--config-file']),

            Opt("default-release", True, False,
                ['-t', '--target-release', '--default-release']),

            Opt("diff-only", False, False,
                ['--diff-only']),

            Opt("download-only", False, False,
                ['-d', '--download-only']),

            Opt("dsc-only", False, False,
                ['--dsc-only']),

            Opt("fix-broken", False, False,
                ['-f', '--fix-broken']),

            Opt("fix-missing", False, False,
                ['-m', '--ignore-missing', '--fix-missing']),

            Opt("force-yes", False, False,
                ['--force-yes']),

            Opt("help", False, False,
                ['-h', '--help']),

            Opt("host-architecture", True, False,
                ['-a', '--host-architecture']),

            Opt("ignore-hold", False, False,
                ['--ignore-hold']),

            Opt("indep-only", False, False,
                ['--indep-only']),

            Opt("install-suggests", False, False,
                ['--install-suggests']),

            Opt("list-cleanup", False, False,
                ['--list-cleanup']),

            Opt("no-allow-insecure-repositories", False, False,
                ['--no-allow-insecure-repositories']),

            Opt("no-download", False, False,
                ['--no-download']),

            Opt("no-install-recommends", False, False,
                ['--no-install-recommends']),

            Opt("no-install-suggests", False, False,
                ['--no-install-suggests']),

            Opt("no-list-cleanup", False, False,
                ['--no-list-cleanup']),

            Opt("no-remove", False, False,
                ['--no-remove']),

            Opt("no-show-upgraded", False, False,
                ['--no-show-upgraded']),

            Opt("no-upgrade", False, False,
                ['--no-upgrade']),

            Opt("only-source", False, False,
                ['--only-source']),

            Opt("only-upgrade", False, False,
                ['--only-upgrade']),

            Opt("option", True, True,
                ['-o', '--option']),

            Opt("print-uris", False, False,
                ['--print-uris']),

            Opt("purge", False, False,
                ['--purge']),

            Opt("quiet", False, False,
                ['-q', '--quiet']),

            Opt("reinstall", False, False,
                ['--reinstall']),

            Opt("show-progress", False, False,
                ['--show-progress']),

            Opt("simulate", False, False,
                ['-s', '--simulate', '--just-print', '--dry-run', '--recon', '--no-act']),

            Opt("tar-only", False, False,
                ['--tar-only']),

            Opt("trivial-only", False, False,
                ['--trivial-only']),

            Opt("verbose-versions", False, False,
                ['-V', '--verbose-versions']),

            Opt("version", False, False,
                ['-v', '--version']),

            Opt("with-new-pkgs", False, False,
                ['--with-new-pkgs']),

            Opt("with-source", True, False,
                ['--with-source'])
        ]

    @classmethod
    @postprocess_opts("--force-yes")
    def postprocess_forceyes(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "force": "yes"
            }
        }

    @classmethod
    @postprocess_opts("--allow-unauthenticated --allow-downgrades")
    def postprocess_allowunauthenticatedallowdowngrades(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "force": "yes"
            }
        }

    @classmethod
    @postprocess_opts("--allow-change-held-packages")
    def postprocess_allowchangeheldpackages(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "--allow-change-held-packages": "yes"
            }
        }

    @classmethod
    @postprocess_opts("--allow-downgrades")
    def postprocess_allowdowngrades(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "allow_downgrade": "yes"
            }
        }

    @classmethod
    @postprocess_opts("--allow-unauthenticated")
    def postprocess_allowunauthenticated(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "allow_unauthenticated": "yes"
            }
        }

    @classmethod
    @postprocess_opts("--autoremove")
    def postprocess_autoremove(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "autoremove": True
            }
        }

    @classmethod
    @postprocess_opts("--assume-yes")
    def postprocess_assumeyes(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--default-release <<value>>")
    def postprocess_defaultreleasevalue(cls, value: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "default_release": value
            }
        }

    @classmethod
    @postprocess_opts("-o Dpkg::Options::=<<value :m>>")
    def postprocess_odpkgoptionsvalue(cls, value: List[str], tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "dpkg_options": ",".join(value)
            }
        }

    @classmethod
    @postprocess_opts("--no-remove")
    def postprocess_noremove(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "fail_on_autoremove": True
            }
        }

    @classmethod
    @postprocess_opts("--list-cleanup")
    def postprocess_listcleanup(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-install-recommends")
    def postprocess_noinstallrecommends(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "install_recommends": False
            }
        }

    @classmethod
    @postprocess_opts("--no-install-suggests")
    def postprocess_noinstallsuggests(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-list-cleanup")
    def postprocess_nolistcleanup(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--no-show-upgraded")
    def postprocess_noshowupgraded(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--only-upgrade")
    def postprocess_onlyupgrade(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "only_upgrade": "yes"
            }
        }

    @classmethod
    @postprocess_opts("--print-uris")
    def postprocess_printuris(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--purge")
    def postprocess_purge(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.apt": {
                "purge": "yes"
            }
        }

    @classmethod
    @postprocess_opts("--quiet")
    def postprocess_quiet(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--verbose-versions")
    def postprocess_verboseversions(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}
