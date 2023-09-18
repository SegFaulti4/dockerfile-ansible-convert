from src.ansible_matcher.commands.template_handler import *


@template_handler("ln -s <<globs : m>> <<dest : p>>")
@postprocess_commands("ln")
def handler_lnsglobsmdestp(globs: List[str], dest: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.stat": {
                "path": dest,
                "follow": False
            },
            "changed_when": False,
            "register": "st_reg"
        },
        {
            "ansible.builtin.shell": {
                "cmd": "realpath -sm {{ files }}",
                "chdir": "{{ dest if dest_is_dir else (dest | dirname) }}"
            },
            "vars": {
                "files": globs,
                "dest": dest,
                "dest_is_dir": "{{ (st_reg.stat.isdir is defined and st_reg.stat.isdir) | ternary(true, false) }}"
            },
            "changed_when": False,
            "register": "ls_reg"
        },
        {
            "ansible.builtin.fail": {
                "msg": "Failed to create symlink - last file is not a directory"
            },
            "when": [
                "ls_reg.stdout_lines | length > 1",
                "st_reg.stat.isdir is undefined or st_reg.stat.isdir == False"
            ]
        },
        {
            "ansible.builtin.file": {
                "state": "link",
                "force": True,
                "follow": False,
                "src": "{{ item }}",
                "path": "{{ ((dest, item | basename) | path_join) if dest_is_dir else dest }}"
            },
            "loop": "{{ ls_reg.stdout_lines }}",
            "vars": {
                "dest": dest,
                "dest_is_dir": "{{ (st_reg.stat.isdir is defined and st_reg.stat.isdir) | ternary(true, false) }}"
            }
        }
    ]


@template_handler("ln -s <<src>>")
@postprocess_commands("ln")
def handler_lnssrc(src: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.file": {
                "state": "link",
                "force": True,
                "follow": False,
                "src": "{{ src }}",
                "path": "{{ (cwd, src | basename) | path_join }}"
            },
            "vars": {
                "cwd": tweaks.cwd,
                "src": src
            }
        }
    ]
