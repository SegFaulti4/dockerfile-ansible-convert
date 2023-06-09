from src.ansible_matcher.main import *
from src.ansible_matcher.opts_extraction import *
from typing import Callable
from abc import ABC
from abc import abstractmethod
import inspect


CommandCallOpts = Dict[str, CommandCallParts]
CommandTemplateOpts = Dict[str, CommandTemplateParts]
_POSTPROCESS_TEMPLATE_KEY = "_postprocess_template"


def _tmpl(s: str) -> Optional[CommandTemplateParts]:
    return TemplateConstructor().from_str(s)


class Opt:
    name: str
    arg_required: bool
    many_args: bool
    aliases: List[str]

    def __init__(self, name: str, arg_req: bool, many_args: bool, aliases: List[str]):
        self.name = name
        self.arg_required = arg_req
        self.many_args = many_args
        self.aliases = aliases


class CommandConfig(ABC):

    @classmethod
    @property
    @abstractmethod
    def entry(cls) -> CommandTemplateParts:
        ...

    @classmethod
    @property
    @abstractmethod
    def opts(cls) -> List[Opt]:
        ...

    # these fields are automatically initialised during inheritance (__init_subclass__)
    _opts_postprocess: List[Tuple[CommandTemplateOpts, Callable]]
    _opts_alias_mapping: Dict[str, Opt]

    def __init_subclass__(cls):
        super().__init_subclass__()

        cls._opts_alias_mapping = dict()
        for opt in cls.opts:
            for alias in opt.aliases:
                cls._opts_alias_mapping[alias] = opt

        def pp_func_predicate(pp_func):
            # might need to check if method accepts argument 'tweaks'
            return inspect.ismethod(pp_func) and hasattr(pp_func, _POSTPROCESS_TEMPLATE_KEY)

        # inspect all opt postprocessing functions
        pp_funcs = [m[1] for m in inspect.getmembers(cls, predicate=pp_func_predicate)]

        cls._opts_postprocess = list()
        for func in pp_funcs:
            extracted_tmpl = cls.extract_command_template(getattr(func, _POSTPROCESS_TEMPLATE_KEY))
            assert extracted_tmpl is not None
            cls._opts_postprocess.append((extracted_tmpl.opts, func))

    @classmethod
    def extract_command_call(cls, comm: CommandCallParts) \
            -> Optional[ExtractedCommandCall]:

        opts_extractor = CommandOptsExtractor(opts_map=cls._opts_alias_mapping)
        tmp = copy.deepcopy(comm)
        return opts_extractor.extract(tmp)

    @classmethod
    def extract_command_template(cls, templ: CommandTemplateParts) \
            -> Optional[ExtractedCommandTemplate]:

        opts_extractor = CommandOptsExtractor(opts_map=cls._opts_alias_mapping)
        tmp = copy.deepcopy(templ)
        return opts_extractor.extract(tmp)

    @classmethod
    def postprocess_command_opts(cls, opts: CommandCallOpts, tweaks: Optional[TemplateTweaks]) \
            -> Tuple[Dict[str, Any], CommandCallOpts]:
        module_params = dict()
        unmatched_opts = {k: v for k, v in opts.items()}

        for tmpl_opts, pp_func in cls._opts_postprocess:
            pp_kwargs = dict()
            for k, v in tmpl_opts.items():
                if k not in opts:
                    pp_kwargs = None
                    break
                v = listify(v)

                if not v and not unmatched_opts[k]:
                    del unmatched_opts[k]
                    continue
                if not v or not unmatched_opts[k]:
                    pp_kwargs = None
                    break

                opt_matcher = CommandTemplateMatcher(template=v, template_tweaks=tweaks)
                match = opt_matcher.match(opts[k])
                if match is None:
                    pp_kwargs = None
                    break
                field_values, unmatched = match

                pp_kwargs = CommandTemplateMatcher.merge_match_results(pp_kwargs, field_values)
                if pp_kwargs is None:
                    break

                if not unmatched:
                    del unmatched_opts[k]
                else:
                    unmatched_opts[k] = unmatched
            if pp_kwargs is not None:
                pp_kwargs['tweaks'] = tweaks
                params = pp_func(**pp_kwargs)
                module_params = merge_dicts(module_params, params, override=False)

        return module_params, unmatched_opts


def opts_postprocess(tmpl_s: str) -> Callable:

    def decorator(func):
        tmpl = _tmpl(tmpl_s)
        assert tmpl is not None

        # attribute is later used to identify opt postprocessing methods
        # and create corresponding command opt template
        setattr(func, _POSTPROCESS_TEMPLATE_KEY, tmpl)
        return func

    return decorator


def register_config(command_name: str):

    def decorator(cls):
        # TODO: register new config somewhere
        return cls

    return decorator


@register_config("apt install")
class AptInstallConfig(CommandConfig):
    entry = _tmpl("apt install <<params : m>>")
    opts = [Opt("option", True, True, ["-o", "--option"])]

    @classmethod
    @opts_postprocess("-o Dpkg::Options::=<<value>>")
    def pp_name(cls, value: str, tweaks: Optional[TemplateTweaks]) -> Dict[str, Any]:
        return {
            "apt": {
                "dpkg_options": value
            }
        }


def main():
    filepath = "/home/popovms/course/dev/sandbox/ansible_matcher/input"
    commands = []
    with open(filepath, "r") as inF:
        commands.extend([line.strip() for line in inF.readlines()])
    if not commands:
        return


if __name__ == "__main__":
    main()
