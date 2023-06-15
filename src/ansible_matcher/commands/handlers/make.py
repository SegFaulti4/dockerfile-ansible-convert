from src.ansible_matcher.commands.template_handler import *


@template_handler("make")
@postprocess_commands("make")
def handler_make(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.make": {
                "chdir": tweaks.cwd
            }
        }
    ]


@template_handler("make <<param : m>>=<<value : m>>")
@postprocess_commands("make")
def handler_makeparammvaluem(param: List[str], value: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.make": {
                "chdir": tweaks.cwd,
                "params": {p: v for p, v in zip(param, value)}
            }
        }
    ]


@template_handler("make <<target>>")
@postprocess_commands("make")
def handler_maketarget(target: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.make": {
                "chdir": tweaks.cwd,
                "target": target
            }
        }
    ]


@template_handler("make <<target>> <<param : m>>=<<value : m>>")
@postprocess_commands("make")
def handler_maketargetparammvaluem(target: str, param: List[str], value: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.make": {
                "chdir": tweaks.cwd,
                "target": target,
                "params": {p: v for p, v in zip(param, value)}
            }
        }
    ]


@template_handler("make <<param : m>>=<<value : m>> <<target>>")
@postprocess_commands("make")
def handler_makeparammvaluemtarget(param: List[str], value: List[str], target: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.make": {
                "chdir": tweaks.cwd,
                "target": target,
                "params": {p: v for p, v in zip(param, value)}
            }
        }
    ]


@template_handler("make <<pre_param : m>>=<<pre_value : m>> <<target>> <<post_param : m>>=<<post_value : m>>")
@postprocess_commands("make")
def handler_makepreparammprevaluemtargetpostparammpostvaluem(pre_param: List[str], pre_value: List[str], target: str, post_param: List[str], post_value: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.make": {
                "chdir": tweaks.cwd,
                "target": target,
                "params": {p: v for p, v in zip(pre_param + post_param, pre_value + post_value)}
            }
        }
    ]

