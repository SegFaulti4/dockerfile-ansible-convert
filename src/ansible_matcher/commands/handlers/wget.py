from src.ansible_matcher.commands.template_handler import *


@template_handler("wget <<url>>")
@postprocess_commands("wget")
def handler_wgeturl(url: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.get_url": {
                "url": "{{ src }}",
                "dest": "{{ (cwd, src | basename) | path_join }}",
                "force": True,
                "decompress": False
            },
            "vars": {
                "cwd": tweaks.cwd,
                "src": url
            }
        }
    ]


@template_handler("wget --tries <<tries>> <<url>>")
@postprocess_commands("wget")
def handler_wgettriestriesurl(tries: str, url: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.get_url": {
                "url": "{{ src }}",
                "dest": "{{ (cwd, src | basename) | path_join }}",
                "force": True,
                "decompress": False
            },
            "vars": {
                "cwd": tweaks.cwd,
                "src": url
            },
            "retries": tries
        }
    ]

