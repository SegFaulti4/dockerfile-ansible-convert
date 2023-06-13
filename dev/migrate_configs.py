import re

from src.ansible_matcher.commands import *
from src.ansible_matcher.template_lang import *


def class_name_wrapper(s: str) -> str:
    s = s.lower()
    s = "".join(sub[0].upper() + sub[1:] for sub in s.split('-'))
    s = "".join(sub[0].upper() + sub[1:] for sub in s.split(' '))
    return s


def opt_repr(opt_name: str, opt: Dict) -> str:
    aliases = opt["aliases"]
    arg_req = opt["arg_required"]
    many_args = opt["many_args"]
    return f'Opt("{opt_name}", {arg_req}, {many_args}, {aliases})'


def postprocess_repr(tmpl_s: str, pp: Dict) -> str:
    pp_name = "postprocess_" + "".join(filter(lambda x: x.isalpha(), tmpl_s)).lower()
    tmpl = TemplateConstructor().from_str(tmpl_s)
    fields = [p for tp in tmpl for p in tp.parts]

    def _proc_str(s: str) -> str:
        if "<<" in s and ">>" in s:
            s = s.replace("<<", "{")
            s = s.replace(">>", "}")
            return f"__pre__{s}__post__"
        return s

    return_val = f'{visit_dict(pp, predicate=lambda x: isinstance(x, str), proc=_proc_str)}'
    return_val = re.compile(r"'__pre__(?P<str>.*?)__post__'").sub(r"f'\g<str>'", return_val)

    res = \
        '\t@classmethod\n' + \
        f'\t@postprocess_opts("{tmpl_s}")\n' + \
        f'\tdef {pp_name}(cls' + (', ' if fields else '') + ', '.join(
            f'{field.name}: ' + ('List[str]' if field.spec_many else 'str') for field in fields) + \
        ', tweaks: TemplateTweaks) -> Dict[str, Any]:\n' + \
        f'\t\treturn {return_val}\n'
    return res


def main():
    path = "./apt-get.json"
    with open(path, "r") as inF:
        config = json.load(inF)

    for comm_name, comm_conf in config.items():
        entry = comm_conf["entry"]
        opts = comm_conf["opts"]
        postprocess = comm_conf["opts_postprocess"]
        text = "from src.new_matcher.main import *\n\n"
        text += \
            f'@command_config("{comm_name}")\n' + \
            f'class {class_name_wrapper(comm_name)}Config(CommandConfig):\n' + \
            f'\tentry: ClassVar[CommandTemplateParts] = tmpl("{entry}")\n' + \
            f'\topts: ClassVar[List[Opt]] = [' + \
            ',\n\t\t\t\t\t\t\t\t '.join(
                opt_repr(opt_name, opt) for opt_name, opt in opts.items()) + ']\n' + \
            '\n' + \
            '\n'.join(postprocess_repr(tmpl, pp) for tmpl, pp in postprocess.items())

        with open(f"./{comm_name}_config.py", "w") as outF:
            outF.write(text)


if __name__ == "__main__":
    main()
    # print(class_name_wrapper('apt-get install'))
