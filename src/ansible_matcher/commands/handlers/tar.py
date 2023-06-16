from src.ansible_matcher.commands.template_handler import *


@template_handler("tar -x -f <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tar_file_directory(file: str, directory: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return [
        {
            "ansible.builtin.unarchive": {
                "src": file,
                "dest": directory,
                "remote_src": "yes"
            }
        }
    ]


@template_handler("tar -x -f <<file : p>>")
@postprocess_commands("tar")
def handler_tar_file(file: str, tweaks: TemplateTweaks) -> AnsibleTasks:
    return handler_tar_file_directory(file=file, directory=tweaks.cwd, tweaks=tweaks)


# some tar opts might be used without '-'
@template_handler("tar <<opts>> <<file : p>> -C <<directory : p>>")
@postprocess_commands("tar")
def handler_tar_pseudo_opts_directory(opts: str, file: str, directory: str, tweaks: TemplateTweaks) \
        -> Optional[AnsibleTasks]:

    if "x" not in opts or "f" not in opts:
        return None
    opts = opts.replace("x", "")
    opts = opts.replace("f", "")

    ignored_opts = ["z", "j", "J", "v", "a"]
    for ign in ignored_opts:
        opts = opts.replace(ign, "")
    if opts:
        return None

    return handler_tar_file_directory(file=file, directory=directory, tweaks=tweaks)


# some tar opts might be used without '-'
@template_handler("tar <<opts>> <<file : p>>")
@postprocess_commands("tar")
def handler_tar_pseudo_opts(opts: str, file: str, tweaks: TemplateTweaks) -> Optional[AnsibleTasks]:
    return handler_tar_pseudo_opts_directory(opts=opts, file=file, directory=tweaks.cwd, tweaks=tweaks)
