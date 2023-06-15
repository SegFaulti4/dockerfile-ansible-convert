from src.ansible_matcher.commands.template_handler import *


@template_handler("pip install <<packages : m>>")
@postprocess_commands("pip install")
def handler_pipinstallpackagesm(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.pip": {
                "name": packages,
                "state": "present",
                "chdir": tweaks.cwd
            }
        }
    ]


@template_handler("pip install -r <<requirement : p>>")
@postprocess_commands("pip install")
def handler_pipinstallrrequirementp(requirement: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.pip": {
                "requirement": requirement,
                "state": "present",
                "chdir": tweaks.cwd
            }
        }
    ]

