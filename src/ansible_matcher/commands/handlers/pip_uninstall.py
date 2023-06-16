from src.ansible_matcher.commands.template_handler import *


@template_handler("pip uninstall <<packages : m>>")
@postprocess_commands("pip uninstall")
def handler_pipuninstallpackagesm(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.pip": {
                "name": packages,
                "state": "absent",
                "chdir": tweaks.cwd
            }
        }
    ]


@template_handler("pip uninstall -r <<requirement : p>>")
@postprocess_commands("pip uninstall")
def handler_pipuninstallrrequirementp(requirement: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.pip": {
                "requirement": requirement,
                "state": "absent",
                "chdir": tweaks.cwd
            }
        }
    ]
