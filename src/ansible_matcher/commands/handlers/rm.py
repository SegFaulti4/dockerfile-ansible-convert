from src.ansible_matcher.commands.template_handler import *


@template_handler("rm <<files : m>>")
@postprocess_commands("rm")
def handler_rmfilesm(files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.shell": {
                "cmd": "realpath -sm {{ files }}",
                "chdir": tweaks.cwd
            },
            "vars": {
                "files": files
            },
            "changed_when": False,
            "register": "ls_reg"
        },
        {
            "ansible.builtin.file": {
                "state": "absent",
                "follow": False,
                "path": "{{ item }}"
            },
            "loop": "{{ ls_reg.stdout_lines }}"
        }
    ]


@template_handler("rm -f <<files : m>>")
@postprocess_commands("rm")
def handler_rmffilesm(files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.shell": {
                "cmd": "realpath -sm {{ files }} 2> /dev/null || true",
                "chdir": tweaks.cwd
            },
            "vars": {
                "files": files
            },
            "changed_when": False,
            "register": "ls_reg"
        },
        {
            "ansible.builtin.file": {
                "state": "absent",
                "follow": False,
                "path": "{{ item }}"
            },
            "loop": "{{ ls_reg.stdout_lines }}"
        }
    ]
