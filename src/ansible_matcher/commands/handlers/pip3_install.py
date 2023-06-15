from src.ansible_matcher.commands.template_handler import *


@template_handler("pip3 install <<packages : m>>")
@postprocess_commands("pip3 install")
def handler_pipinstallpackagesm(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.pip": {
                "name": packages,
                "state": "present",
                "chdir": tweaks.cwd,
                "executable": "pip3"
            }
        }
    ]


@template_handler("pip3 install -r <<requirement : p>>")
@postprocess_commands("pip3 install")
def handler_pipinstallrrequirementp(requirement: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.pip": {
                "requirement": requirement,
                "state": "present",
                "chdir": tweaks.cwd,
                "executable": "pip3"
            }
        }
    ]

