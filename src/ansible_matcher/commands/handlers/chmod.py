from src.ansible_matcher.commands.template_handler import *


@template_handler("chmod <<mode>> <<files : m>>")
@postprocess_commands("chmod")
def handler_chmodmodefilesm(mode: str, files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
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
                "path": "{{ item }}",
                "recurse": False,
                "follow": True,
                "mode": mode
            },
            "loop": "{{ ls_reg.stdout_lines }}"
        }
    ]


@template_handler("chmod -R <<mode>> <<files : m>>")
@postprocess_commands("chmod")
def handler_chmodrmodefilesm(mode: str, files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
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
            "ansible.builtin.stat": {
                "follow": False,
                "path": "{{ item }}"
            },
            "loop": "{{ ls_reg.stdout_lines }}",
            "register": "st_reg"
        },
        {
            "ansible.builtin.file": {
                "state": "{{ (item.stat.isdir is defined and item.stat.isdir) | ternary('directory', 'file') }}",
                "recurse": "{{ (item.stat.isdir is defined and item.stat.isdir) | ternary(true, false) }}",
                "follow": "{{ (item.stat.isdir is defined and item.stat.isdir) | ternary(false, true) }}",
                "path": "{{ item.stat.path }}",
                "mode": mode
            },
            "loop": "{{ st_reg.results }}"
        }
    ]

