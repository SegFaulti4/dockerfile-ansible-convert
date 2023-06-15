from src.ansible_matcher.commands.template_handler import *


@template_handler("useradd <<name>>")
@postprocess_commands("useradd")
def handler_useraddname(name: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.group": {
                "state": "present",
                "name": name
            }
        },
        {
            "ansible.builtin.user": {
                "state": "present",
                "name": name,
                "group": name,
                "create_home": False
            }
        }
    ]


@template_handler("useradd --no-user-group <<name>>")
@postprocess_commands("useradd")
def handler_useraddnousergroupname(name: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.user": {
                "state": "present",
                "name": name,
                "create_home": False
            }
        }
    ]

