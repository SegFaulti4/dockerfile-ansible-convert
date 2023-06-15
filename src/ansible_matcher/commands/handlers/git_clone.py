from src.ansible_matcher.commands.template_handler import *


@template_handler("git clone <<repo>>")
@postprocess_commands("git clone")
def handler_gitclonerepo(repo: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.git": {
                "repo": "{{ repo }}",
                "dest": "{{ (dir, repo | basename | regex_replace('.git$')) | path_join }}",
                "clone": True,
                "recursive": False
            },
            "vars": {
                "dir": tweaks.cwd,
                "repo": repo
            }
        }
    ]


@template_handler("git clone <<repo>> <<directory : p>>")
@postprocess_commands("git clone")
def handler_gitclonerepodirp(repo: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.git": {
                "repo": repo,
                "dest": directory,
                "clone": True,
                "recursive": False
            }
        }
    ]

