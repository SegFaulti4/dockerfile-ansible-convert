from src.ansible_matcher.commands.command_config import *


@command_config("useradd")
class UseraddConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("useradd <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("base dir", True, False,
                ['-b', '--base-dir']),

            Opt("comment", True, False,
                ['-c', '--comment']),

            Opt("create home", False, False,
                ['-m', '--create-home']),

            Opt("home dir", True, False,
                ['-d', '--home-dir', '--home']),

            Opt("default", False, False,
                ['-D', '--defaults']),

            Opt("primary group", True, False,
                ['-g', '--gid']),

            Opt("supplementary groups", True, False,
                ['-G', '--groups']),

            Opt("skeleton directory", True, False,
                ['-k', '--skel']),

            Opt("key", True, True,
                ['-K', '--key']),

            Opt("no log init", False, False,
                ['-l', '--no-log-init']),

            Opt("no create home", False, False,
                ['-M', '--no-create-home']),

            Opt("system", False, False,
                ['-r', '--system']),

            Opt("shell", True, False,
                ['-s', '--shell']),

            Opt("user group", False, False,
                ['-U', '--user-group']),

            Opt("no user group", False, False,
                ['-N', '--no-user-group']),

            Opt("non unique", False, False,
                ['-o', '--non-unique']),

            Opt("uid", True, False,
                ['-u', '--uid']),

            Opt("password", True, False,
                ['-p', '--password'])
        ]

    @classmethod
    @postprocess_opts("--user-group")
    def postprocess_usergroup(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {}

    @classmethod
    @postprocess_opts("--base-dir <<directory : p>>")
    def postprocess_basedirdirp(cls, directory: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "home": f"{{ ('{directory}', username) | path_join }}"
            }
        }

    @classmethod
    @postprocess_opts("--comment <<comment>>")
    def postprocess_commentcomment(cls, comment: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "comment": comment
            }
        }

    @classmethod
    @postprocess_opts("--create-home")
    def postprocess_createhome(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "create_home": True
            }
        }

    @classmethod
    @postprocess_opts("--home-dir <<dir : p>>")
    def postprocess_homedirdirp(cls, directory: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "home": directory
            }
        }

    @classmethod
    @postprocess_opts("--gid <<group>>")
    def postprocess_gidgroup(cls, group: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "group": group
            }
        }

    @classmethod
    @postprocess_opts("--groups <<groups>>")
    def postprocess_groupsgroups(cls, groups: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "groups": groups,
                "append": True
            }
        }

    @classmethod
    @postprocess_opts("--skel <<dir : p>>")
    def postprocess_skeldirp(cls, directory: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "skeleton": directory
            }
        }

    @classmethod
    @postprocess_opts("--no-create-home")
    def postprocess_nocreatehome(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "create_home": False
            }
        }

    @classmethod
    @postprocess_opts("--system")
    def postprocess_system(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "system": True
            }
        }

    @classmethod
    @postprocess_opts("--shell <<shell>>")
    def postprocess_shellshell(cls, shell: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "shell": shell
            }
        }

    @classmethod
    @postprocess_opts("--non-unique")
    def postprocess_nonunique(cls, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "non_unique": True
            }
        }

    @classmethod
    @postprocess_opts("--uid <<uid>>")
    def postprocess_uiduid(cls, uid: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "uid": uid
            },
            "ansible.builtin.group": {
                "gid": uid
            }
        }

    @classmethod
    @postprocess_opts("--password <<password>>")
    def postprocess_passwordpassword(cls, password: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "ansible.builtin.user": {
                "password": password
            }
        }
