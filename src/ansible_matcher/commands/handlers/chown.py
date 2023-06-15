from src.ansible_matcher.commands.template_handler import *


@template_handler("chown <<owner>>:<<group>> <<files : m>>")
@postprocess_commands("chown")
def handler_chownownergroupfilesm(owner: str, group: str, files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
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
                "owner": owner,
                "group": group
            },
            "loop": "{{ ls_reg.stdout_lines }}"
        }
    ]


@template_handler("chown <<owner>> <<files : m>>")
@postprocess_commands("chown")
def handler_chownownerfilesm(owner: str, files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.shell": {
                "cmd": "realpath -sm {{ files }}",
                "chdir": tweaks.cwd
            },
            "vars": {
                "files": f'{files}'
            },
            "changed_when": False,
            "register": "ls_reg"
        },
        {
            "ansible.builtin.file": {
                "path": "{{ item }}",
                "recurse": False,
                "follow": True,
                "owner": owner
            },
            "loop": "{{ ls_reg.stdout_lines }}"
        }
    ]


@template_handler("chown -R <<owner>>:<<group>> <<files : m>>")
@postprocess_commands("chown")
def handler_chownrownergroupfilesm(owner: str, group: str, files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.shell": {
                "cmd": "realpath -sm {{ files }}",
                "chdir": tweaks.cwd
            },
            "vars": {
                "files": f'{files}'
            },
            "changed_when": False,
            "register": "ls_reg"
        },
        {
            "ansible.builtin.stat": {
                "follow": False,
                "path": "{{ item }}"
            },
            "changed_when": False,
            "loop": "{{ ls_reg.stdout_lines }}",
            "register": "st_reg"
        },
        {
            "ansible.builtin.file": {
                "state": "{{ (item.stat.isdir is defined and item.stat.isdir) | ternary('directory', 'file') }}",
                "recurse": "{{ (item.stat.isdir is defined and item.stat.isdir) | ternary(true, false) }}",
                "follow": False,
                "path": "{{ item.stat.path }}",
                "owner": owner,
                "group": group
            },
            "loop": "{{ st_reg.results }}"
        }
    ]


@template_handler("chown -R <<owner>> <<files : m>>")
@postprocess_commands("chown")
def handler_chownrownerfilesm(owner: str, files: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
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
            "changed_when": False,
            "loop": "{{ ls_reg.stdout_lines }}",
            "register": "st_reg"
        },
        {
            "ansible.builtin.file": {
                "state": "{{ (item.stat.isdir is defined and item.stat.isdir) | ternary('directory', 'file') }}",
                "recurse": "{{ (item.stat.isdir is defined and item.stat.isdir) | ternary(true, false) }}",
                "follow": False,
                "path": "{{ item.stat.path }}",
                "owner": owner
            },
            "loop": "{{ st_reg.results }}"
        }
    ]

