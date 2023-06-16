from src.ansible_matcher.commands.template_handler import *


@template_handler("mv <<globs : m>> <<dest : p>>")
@postprocess_commands("mv")
def handler_mvglobsmdestp(globs: List[str], dest: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "name": "Inspect 'mv' parameters",
            "vars": {
                "sources": globs,
                "destination": dest
            },
            "block": [
                {
                    "name": "Resolve 'mv' source paths",
                    "ansible.builtin.shell": {
                        "cmd": "realpath -se {{ sources }}",
                        "chdir": tweaks.cwd
                    },
                    "changed_when": False,
                    "register": "src_paths"
                },
                {
                    "name": "Inspect 'mv' destination",
                    "ansible.builtin.stat": {
                        "path": "{{ destination }}",
                        "follow": False
                    },
                    "changed_when": False,
                    "register": "dst_info"
                },
                {
                    "name": "Fail 'mv' if multiple sources and destination is not a directory",
                    "ansible.builtin.fail": {
                        "msg": "Failed to move files"
                    },
                    "when": [
                        "src_paths.stdout_lines | length > 1",
                        "dst_info.stat.isdir is undefined or dst_info.stat.isdir == False"
                    ]
                }
            ]
        },
        {
            "name": "Handle 'mv' single source",
            "when": "src_paths.stdout_lines | length == 1",
            "vars": {
                "raw_dest": dest,
                "source": "{{ src_paths.stdout_lines[0] }}",
                "destination": "{{ raw_dest | regex_replace('/$') }}"
            },
            "block": [
                {
                    "name": "Inspect 'mv' single source",
                    "ansible.builtin.stat": {
                        "path": "{{ source }}",
                        "follow": False
                    },
                    "changed_when": False,
                    "register": "src_info"
                },
                {
                    "name": "Handle 'mv' rename directory",
                    "when": [
                        "src_info.stat.isdir == True",
                        "dst_info.stat.isdir is undefined"
                    ],
                    "block": [
                        {
                            "file": {
                                "path": "{{ destination }}",
                                "state": "directory"
                            }
                        },
                        {
                            "copy": {
                                "src": "{{ source }}/",
                                "dest": "{{ destination }}",
                                "remote_src": True,
                                "force": True
                            }
                        }
                    ]
                },
                {
                    "name": "Copy file or directory",
                    "when": "src_info.stat.isdir == False or dst_info.stat.isdir is defined",
                    "copy": {
                        "src": "{{ source }}",
                        "dest": "{{ destination }}",
                        "remote_src": True,
                        "force": True
                    }
                }
            ]
        },
        {
            "name": "Handle 'mv' multiple sources",
            "when": "src_paths.stdout_lines | length > 1",
            "vars": {
                "raw_dest": dest,
                "sources": "{{ src_paths.stdout_lines }}",
                "destination": "{{ raw_dest | regex_replace('/$') }}"
            },
            "loop": "{{ sources }}",
            "copy": {
                "src": "{{ item }}",
                "dest": "{{ destination }}",
                "remote_src": True,
                "force": True
            }
        },
        {
            "name": "Remove 'mv' sources",
            "vars": {
                "sources": "{{ src_paths.stdout_lines }}"
            },
            "loop": "{{ sources }}",
            "ansible.builtin.file": {
                "path": "{{ item }}",
                "follow": False,
                "state": "absent"
            }
        }
    ]
