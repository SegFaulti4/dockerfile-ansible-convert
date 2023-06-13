from src.ansible_matcher.main import *
from src.ansible_matcher.opts_extraction import *
from typing import Callable, ClassVar, Type
from abc import ABC
from abc import abstractmethod
import inspect


CommandCallOpts = Dict[str, CommandCallParts]
CommandTemplateOpts = Dict[str, CommandTemplateParts]
AnsibleTasks = List[Dict[str, Any]]

_OPTS_POSTPROCESS_ATTR_KEY = "_opts_tmpl"
_TEMPLATE_HANDLER_ATTR_KEY = '_postprocess_configs'


def _tmpl(s: str) -> Optional[CommandTemplateParts]:
    return TemplateConstructor().from_str(s)


# TODO: move this to opts extraction
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


# TODO: move this to opts extraction
def match_extracted_call(extracted_call: ExtractedCommandCall, extracted_tmpl: ExtractedCommandTemplate,
                         template_tweaks: TemplateTweaks) -> Optional[Tuple[TemplateMatchResult, CommandCallOpts]]:
    params_matcher = CommandTemplateMatcher(template=extracted_tmpl.params, template_tweaks=template_tweaks)
    params_fields = params_matcher.full_match(extracted_call.params)
    if params_fields is None:
        return None

    opt_match = match_extracted_call_opts(extracted_call.opts, extracted_tmpl.opts, template_tweaks=template_tweaks)
    if opt_match is None:
        return None
    opt_fields, unmatched_opts = opt_match

    match_res = CommandTemplateMatcher.merge_match_results(params_fields, opt_fields)
    if match_res is None:
        return None

    return match_res, unmatched_opts


# TODO: move this to opts extraction
def match_extracted_call_opts(call_opts: CommandCallOpts, tmpl_opts: CommandTemplateOpts,
                              template_tweaks: TemplateTweaks) -> Optional[Tuple[TemplateMatchResult, CommandCallOpts]]:
    opt_fields = dict()
    unmatched_opts = {k: listify(v) for k, v in call_opts.items()}

    for k, v in tmpl_opts.items():
        if k not in call_opts:
            return None
        v = listify(v)

        if not v and not unmatched_opts[k]:
            del unmatched_opts[k]
            continue
        if not v or not unmatched_opts[k]:
            return None

        opt_matcher = CommandTemplateMatcher(template=v, template_tweaks=template_tweaks)
        opt_match = opt_matcher.match(call_opts[k])
        if opt_match is None:
            return None
        tmp_fields, unmatched = opt_match

        opt_fields = CommandTemplateMatcher.merge_match_results(opt_fields, tmp_fields)
        if opt_fields is None:
            return None

        if not unmatched:
            del unmatched_opts[k]
        else:
            unmatched_opts[k] = unmatched

    return opt_fields, unmatched_opts


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
            return inspect.ismethod(pp_func) and hasattr(pp_func, _OPTS_POSTPROCESS_ATTR_KEY)

        # inspect all opt postprocessing functions
        pp_funcs = [m[1] for m in inspect.getmembers(cls, predicate=pp_func_predicate)]

        cls._opts_postprocess = list()
        for func in pp_funcs:
            extracted_tmpl = cls._extract(getattr(func, _OPTS_POSTPROCESS_ATTR_KEY))
            assert extracted_tmpl is not None
            cls._opts_postprocess.append((extracted_tmpl.opts, func))

    @classmethod
    def check_entry(cls, comm: Union[CommandCallParts, CommandTemplateParts]) -> bool:
        matcher = CommandTemplateMatcher(template=cls.entry)
        match = matcher.full_match(comm)

        if match is None:
            return False
        return True

    @classmethod
    def extract_command_call(cls, comm: CommandCallParts) \
            -> Optional[ExtractedCommandCall]:
        if not cls.check_entry(comm):
            return None

        return cls._extract(comm)

    @classmethod
    def extract_command_template(cls, tmpl: CommandTemplateParts) \
            -> Optional[ExtractedCommandTemplate]:
        if not cls.check_entry(tmpl):
            return None

        return cls._extract(tmpl)

    @classmethod
    def _extract(cls, comm: Union[CommandCallParts, CommandTemplateParts]) \
            -> Optional[Union[ExtractedCommandCall, ExtractedCommandTemplate]]:
        opts_extractor = CommandOptsExtractor(opts_map=cls._opts_alias_mapping)
        tmp = copy.deepcopy(comm)
        return opts_extractor.extract(tmp)

    @classmethod
    def postprocess_command_opts(cls, call_opts: CommandCallOpts, tweaks: TemplateTweaks) \
            -> Tuple[Dict[str, Any], CommandCallOpts]:
        module_params = dict()
        unmatched_opts = {k: listify(v) for k, v in call_opts.items()}

        for tmpl_opts, pp_func in cls._opts_postprocess:
            if not unmatched_opts:
                break
            matched = match_extracted_call_opts(unmatched_opts, tmpl_opts, template_tweaks=tweaks)
            if matched is None:
                continue
            pp_kwargs, unmatched_opts = matched
            params = pp_func(tweaks=tweaks, **pp_kwargs)
            module_params = merge_dicts(module_params, params, override=False)

        return module_params, unmatched_opts


class CommandConfigRegistry:
    RegistryEntry = Tuple[str, Type[CommandConfig]]

    configurations: Dict[str, Type[CommandConfig]]
    config_cache: Dict[str, List[RegistryEntry]]

    def __init__(self):
        self.configurations = dict()
        self.config_cache = dict()

    def add_entry(self, command_name: str, config_cls: Type[CommandConfig]) -> None:
        assert command_name not in self.configurations
        self.configurations[command_name] = config_cls

        first_part: TemplatePart = config_cls.entry[0]
        # in order for new config to be cached
        # the first part from command's 'entry' should be a constant string
        assert not first_part.parts
        if first_part.value not in self.config_cache:
            self.config_cache[first_part.value] = list()
        self.config_cache[first_part.value].append((command_name, config_cls))

    def fetch_by_command(self, comm: CommandCallParts) -> List[RegistryEntry]:
        # ignoring commands that have parameter in first word
        if comm[0].parts:
            return []
        return self.config_cache.get(comm[0].value, [])

    def fetch_by_name(self, command_name: str) -> Optional[RegistryEntry]:
        return self.configurations.get(command_name, None)


global_command_config_entry = CommandConfigRegistry()


def postprocess_opts(tmpl_s: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        tmpl = _tmpl(tmpl_s)
        assert tmpl is not None

        # attribute is later used to identify opt postprocessing methods
        # and create corresponding command opt template
        setattr(func, _OPTS_POSTPROCESS_ATTR_KEY, tmpl)

        # TODO: check if func accepts argument 'tweaks'
        # TODO: check if other arguments of func correspond
        #  to fields from template and have desired type (list or str)
        return func

    return decorator


class TemplateHandlerRegistry:
    templates: List[Tuple[CommandTemplateParts, Callable]]
    template_cache: Dict[str, List[Tuple[CommandTemplateParts, Callable]]]

    def __init__(self):
        self.templates = list()
        self.template_cache = dict()

    def add_entry(self, command_template: CommandTemplateParts, tmpl_handler: Callable) -> None:
        self.templates.append((command_template, tmpl_handler))

        first_part: TemplatePart = command_template[0]
        # in order for new template to be cached
        # the first template part should be a constant string
        assert not first_part.parts
        if first_part.value not in self.template_cache:
            self.template_cache[first_part.value] = list()
        self.template_cache[first_part.value].append((command_template, tmpl_handler))

    def fetch_by_command(self, comm: CommandCallParts) -> List[Tuple[CommandTemplateParts, Callable, List[str]]]:
        if comm[0].parts:
            return []
        cached = self.template_cache.get(comm[0].value, [])
        res = []
        for tmpl, handler_func in cached:
            postprocess_configs = getattr(handler_func, _TEMPLATE_HANDLER_ATTR_KEY)
            res.append((tmpl, handler_func, postprocess_configs))
        return res


global_template_handler_registry = TemplateHandlerRegistry()


def command_config(command_name: str):
    def decorator(cls):
        global_command_config_entry.add_entry(command_name=command_name, config_cls=cls)
        return cls

    return decorator


@command_config("apt install")
class AptInstallConfig(CommandConfig):
    entry: ClassVar[CommandTemplateParts] = _tmpl("apt install <<params : m>>")
    opts: ClassVar[List[Opt]] = [Opt("option", True, True, ["-o", "--option"])]

    @classmethod
    @postprocess_opts("-o Dpkg::Options::=<<value>>")
    def pp_name(cls, value: str, tweaks: TemplateTweaks) -> Dict[str, Any]:
        return {
            "apt": {
                "dpkg_options": value
            }
        }


def template_handler(tmpl_s: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        tmpl = _tmpl(tmpl_s)
        assert tmpl is not None
        global_template_handler_registry.add_entry(command_template=tmpl, tmpl_handler=func)
        return func

    return decorator


def postprocess_commands(*args: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        setattr(func, _TEMPLATE_HANDLER_ATTR_KEY, list(args))
        return func

    return decorator


@template_handler("apt install <<packages : m>>")
@postprocess_commands("apt install")
def apt_install(packages: List[str], tweaks: TemplateTweaks) -> AnsibleTasks:
    return [{
        "apt": {
            "state": "present",
            "name": packages,
            "force_apt_get": True
        }
    }]
