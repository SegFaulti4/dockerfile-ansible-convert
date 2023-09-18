from src.ansible_matcher.commands.template_handler import *


@template_handler("mkdir -p <<directory : p>>")
@postprocess_commands("mkdir")
def handler_mkdirpdirectoryp(directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.file": {
                "path": directory,
                "state": "directory"
            }
        }
    ]


@template_handler("mkdir <<directory : p>>")
@postprocess_commands("mkdir")
def handler_mkdirdirectoryp(directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.file": {
                "path": directory,
                "state": "directory"
            }
        }
    ]


@template_handler("mkdir -p <<directories : mp>>")
@postprocess_commands("mkdir")
def handler_mkdirpdirectoriesmp(directories: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.file": {
                "path": "{{ item }}",
                "state": "directory"
            },
            "loop": directories
        }
    ]


@template_handler("mkdir <<directories : mp>>")
@postprocess_commands("mkdir")
def handler_mkdirdirectoriesmp(directories: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.file": {
                "path": "{{ item }}",
                "state": "directory"
            },
            "loop": directories
        }
    ]
