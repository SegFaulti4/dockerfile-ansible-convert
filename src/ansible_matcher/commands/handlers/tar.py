from src.ansible_matcher.commands.template_handler import *


@template_handler("tar -x -f <<file : p>>")
@postprocess_commands("tar")
def handler_tarxffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar -x -f <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar fxv <<file : p>>")
@postprocess_commands("tar")
def handler_tarfxvfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar fxv <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarfxvfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar fzx <<file : p>>")
@postprocess_commands("tar")
def handler_tarfzxfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar fzx <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarfzxfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar jxf <<file : p>>")
@postprocess_commands("tar")
def handler_tarjxffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar jxf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarjxffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar jxvf <<file : p>>")
@postprocess_commands("tar")
def handler_tarjxvffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar jxvf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarjxvffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar vxf <<file : p>>")
@postprocess_commands("tar")
def handler_tarvxffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar vxf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarvxffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar vxzf <<file : p>>")
@postprocess_commands("tar")
def handler_tarvxzffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar vxzf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarvxzffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xaf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxaffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xaf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxaffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfa <<file : p>>")
@postprocess_commands("tar")
def handler_tarxfafilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfa <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxfafilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfj <<file : p>>")
@postprocess_commands("tar")
def handler_tarxfjfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfj <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxfjfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfv <<file : p>>")
@postprocess_commands("tar")
def handler_tarxfvfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfv <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxfvfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfvz <<file : p>>")
@postprocess_commands("tar")
def handler_tarxfvzfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfvz <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxfvzfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfx <<file : p>>")
@postprocess_commands("tar")
def handler_tarxfxfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfx <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxfxfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfz <<file : p>>")
@postprocess_commands("tar")
def handler_tarxfzfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfz <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxfzfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfzv <<file : p>>")
@postprocess_commands("tar")
def handler_tarxfzvfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xfzv <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxfzvfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xjf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxjffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xjf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxjffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xJf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxjffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xJf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxjffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xjvf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxjvffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xjvf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxjvffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvaf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvaffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvaf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvaffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvfj <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvfjfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvfj <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvfjfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvfJ <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvfjfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvfJ <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvfjfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvfz <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvfzfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvfz <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvfzfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvjf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvjffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvjf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvjffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvJf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvjffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvJf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvjffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvvf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvvffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvvf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvvffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvzf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxvzffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xvzf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxvzffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xzf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxzffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xzf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxzffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xzfv <<file : p>>")
@postprocess_commands("tar")
def handler_tarxzfvfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xzfv <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxzfvfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxf <<file : p>>")
@postprocess_commands("tar")
def handler_tarzxffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarzxffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxfv <<file : p>>")
@postprocess_commands("tar")
def handler_tarzxfvfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxfv <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarzxfvfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxv <<file : p>>")
@postprocess_commands("tar")
def handler_tarzxvfilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxv <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarzxvfilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxvf <<file : p>>")
@postprocess_commands("tar")
def handler_tarzxvffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zxvf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarzxvffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xzvf <<file : p>>")
@postprocess_commands("tar")
def handler_tarxzvffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar xzvf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarxzvffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zvxf <<file : p>>")
@postprocess_commands("tar")
def handler_tarzvxffilep(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": tweaks.cwd,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar zvxf <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tarzvxffilepcdirectoryp(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": f'{file}',
                "dest": f'{directory}',
                "remote_src": "yes"
            }
        }
    ]

