from src.ansible_matcher.commands.template_handler import *


@template_handler("apk update")
@postprocess_commands("apk")
def handler_apkupdate(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.apk": {
                "update_cache": "yes"
            }
        }
    ]


@template_handler("apk add <<packages : m>>")
@postprocess_commands("apk")
def handler_apkaddpackagesm(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.apk": {
                "name": packages
            }
        }
    ]


@template_handler("apk del <<packages : m>>")
@postprocess_commands("apk")
def handler_apkdelpackagesm(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.apk": {
                "name": packages,
                "state": "absent"
            }
        }
    ]


@template_handler("apk upgrade")
@postprocess_commands("apk")
def handler_apkupgrade(tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "community.general.apk": {
                "upgrade": "yes"
            }
        }
    ]

