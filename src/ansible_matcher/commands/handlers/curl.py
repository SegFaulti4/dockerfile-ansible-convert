from src.ansible_matcher.commands.template_handler import *


@template_handler("curl -o <<output : p>> git.io/scope")
@postprocess_commands("curl")
def handler_curlooutputpgitioscope(output: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.uri": {
                "method": "GET",
                "dest": output,
                "url": "https://git.io/scope"
            }
        }
    ]


@template_handler("curl -o <<output : p>> <<url>>")
@postprocess_commands("curl")
def handler_curlooutputpurl(output: str, url: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.uri": {
                "method": "GET",
                "dest": output,
                "url": url
            }
        }
    ]


@template_handler("curl -O <<url>>")
@postprocess_commands("curl")
def handler_curlourl(url: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.uri": {
                "method": "GET",
                "dest": tweaks.cwd,
                "url": url
            }
        }
    ]
