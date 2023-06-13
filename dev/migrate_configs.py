import re

from src.ansible_matcher.commands import *
from src.ansible_matcher.template_lang import *


def class_name_wrapper(s: str) -> str:
    s = s.lower()
    s = "".join(sub[0].upper() + sub[1:] for sub in s.split('-'))
    s = "".join(sub[0].upper() + sub[1:] for sub in s.split(' '))
    return s


def file_title_wrapper(s: str) -> str:
    s = s.lower()
    s = "_".join(s.split('-'))
    s = "_".join(s.split(' '))
    return s


def opt_repr(opt_name: str, opt: Dict) -> str:
    aliases = opt["aliases"]
    arg_req = opt["arg_required"]
    many_args = opt["many_args"]
    return f'Opt("{opt_name}", {arg_req}, {many_args}, {aliases})'


def dict_template_repr(dict_tmpl: Union[Dict, List[Dict]]) -> str:
    pre = "__pre__"
    post = "__post__"

    def _proc_str(s: str) -> str:
        if "<<" in s and ">>" in s:
            s = s.replace("<<", "{")
            s = s.replace(">>", "}")
            return f"{pre}{s}{post}"
        return s

    if isinstance(dict_tmpl, list):
        return_val = [visit_dict(d, predicate=lambda x: isinstance(x, str), proc=_proc_str)
                      for d in dict_tmpl]
    else:
        return_val = visit_dict(dict_tmpl, predicate=lambda x: isinstance(x, str), proc=_proc_str)

    return_val = json.dumps(return_val, indent=4)

    # WARNING: replacement of multi-arg fields is more complicated
    # TODO: correct values of multi-arg fields manually in generated code
    return_val = re.compile(fr'"{pre}(?P<str>.*?){post}"').sub(r"f'\g<str>'", return_val)
    return_val = return_val.replace(": true", ": True")
    return_val = return_val.replace(": false", ": False")
    return return_val


def indent_value(value: str, tabs: int) -> str:
    return "\n".join("    " * tabs + v for v in value.split("\n"))


def postprocess_repr(tmpl_s: str, module_params: Dict) -> str:
    pp_name = "postprocess_" + "".join(filter(lambda x: x.isalpha(), tmpl_s)).lower()
    tmpl = TemplateConstructor().from_str(tmpl_s)
    fields = [p for tp in tmpl for p in tp.parts]
    return_val = "return " + dict_template_repr(module_params)

    return '    @classmethod\n' + \
        f'    @postprocess_opts("{tmpl_s}")\n' + \
        f'    def {pp_name}(cls' + (', ' if fields else '') + ', '.join(
            f'{field.name}: ' + ('List[str]' if field.spec_many else 'str') for field in fields) + \
        ', tweaks: TemplateTweaks) -> Dict[str, Any]:\n' + \
        f'{indent_value(return_val, tabs=2)}\n'


def template_handler_repr(comm_name: str, tmpl_s: str, tasks: List[Dict]) -> str:
    handler_name = "handler_" + "".join(filter(lambda x: x.isalpha(), tmpl_s)).lower()
    tmpl = TemplateConstructor().from_str(tmpl_s)
    fields = [p for tp in tmpl for p in tp.parts]
    return_val = "return " + dict_template_repr(tasks)

    return f'@template_handler("{tmpl_s}")\n' + \
        f'@postprocess_commands("{comm_name}")\n' + \
        f'def {handler_name}(' + ', '.join(
            f'{field.name}: ' + ('List[str]' if field.spec_many else 'str') for field in fields) + \
        (', ' if fields else '') + 'tweaks: TemplateTweaks) -> AnsibleTasks:\n' + \
        f'{indent_value(return_val, tabs=1)}\n'


def command_config_code(comm_name: str, entry: str, opts: Dict, postprocess: Dict) -> str:
    text = "from src.new_matcher.main import *\n\n\n"
    text += \
        f'@command_config("{comm_name}")\n' + \
        f'class {class_name_wrapper(comm_name)}Config(CommandConfig):\n' + \
        f'    entry: ClassVar[CommandTemplateParts] = tmpl("{entry}")\n' + \
        f'    opts: ClassVar[List[Opt]] = [\n' + \
        ',\n'.join(
            '        ' + opt_repr(opt_name, opt) for opt_name, opt in opts.items()) + '\n    ]\n' + \
        '\n' + \
        '\n'.join(postprocess_repr(tmpl, pp) for tmpl, pp in postprocess.items())
    return text


def template_handlers_code(comm_name: str, examples: Dict[str, List[Dict]]) -> str:
    text = "from src.new_matcher.main import *\n\n\n"
    text += \
        "\n\n".join(template_handler_repr(comm_name=comm_name, tmpl_s=tmpl_s, tasks=tasks)
                    for tmpl_s, tasks in examples.items()) + \
        "\n"
    return text


def main():
    path = "./apt-get.json"
    with open(path, "r") as inF:
        config = json.load(inF)

    for comm_name, comm_conf in config.items():
        entry = comm_conf["entry"]
        opts = comm_conf["opts"]
        postprocess = comm_conf["opts_postprocess"]
        examples = comm_conf["examples"]

        config_text = command_config_code(comm_name=comm_name, entry=entry, opts=opts, postprocess=postprocess)
        with open(f"./{file_title_wrapper(comm_name)}_config.py", "w") as outF:
            outF.write(config_text)

        handlers_text = template_handlers_code(comm_name=comm_name, examples=examples)
        with open(f"./{file_title_wrapper(comm_name)}_handlers.py", "w") as outF:
            outF.write(handlers_text)


if __name__ == "__main__":
    main()
    # print(class_name_wrapper('apt-get install'))
