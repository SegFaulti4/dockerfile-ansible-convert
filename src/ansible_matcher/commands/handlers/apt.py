from src.ansible_matcher.commands.template_handler import *


@template_handler("apt-get install <<pkg_string>>")
@postprocess_commands("apt")
def handler_aptgetinstallpkgstring(pkg_string: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    packages = pkg_string.split()
    return [
        {
            "ansible.builtin.apt": {
                "name": packages[0] if len(packages) == 1 else packages
            }
        }
    ]


@template_handler("apt-get install <<packages : m>>")
@postprocess_commands("apt")
def handler_aptgetinstallpackagesm(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "name": packages,
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get autoclean")
@postprocess_commands("apt")
def handler_aptgetautoclean(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "autoclean": True,
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get clean")
@postprocess_commands("apt")
def handler_aptgetclean(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "clean": True,
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get autoremove")
@postprocess_commands("apt")
def handler_aptgetautoremove(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "autoremove": "yes",
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get build-dep <<packages : m>>")
@postprocess_commands("apt")
def handler_aptgetbuilddeppackagesm(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "name": packages,
                "state": "build-dep",
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get dist-upgrade")
@postprocess_commands("apt")
def handler_aptgetdistupgrade(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "upgrade": "dist",
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get remove <<pkg :m>>")
@postprocess_commands("apt")
def handler_aptgetremovepkgm(pkg: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "name": pkg,
                "state": "absent",
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get update")
@postprocess_commands("apt")
def handler_aptgetupdate(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "update_cache": "yes",
                "force_apt_get": True
            }
        }
    ]


@template_handler("apt-get upgrade")
@postprocess_commands("apt")
def handler_aptgetupgrade(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.apt": {
                "upgrade": "yes",
                "force_apt_get": True
            }
        }
    ]

