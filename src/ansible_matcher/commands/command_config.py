import inspect
import copy
from abc import ABC, abstractmethod
from typing import Optional, Union, Any, Callable, Type, Tuple, List, Dict, ClassVar

from src.ansible_matcher.template_lang.main import \
    TemplateMatcher, CommandWords, TemplateWords, TemplatePart, TemplateTweaks, tmpl_s
from src.ansible_matcher.extracted_matching.opts_extraction import \
    Opt, CommandOpts, TemplateOpts, OptsExtractor
from src.ansible_matcher.extracted_matching.main import match_extracted_call_opts
from src.ansible_matcher.utils import listify, merge_dicts


_OPTS_POSTPROCESS_ATTR_KEY = "_opts_tmpl"


class CommandConfigABC(ABC):

    # entry: ClassVar[CommandTemplateParts] = NotImplemented

    @classmethod
    @property
    @abstractmethod
    def entry(cls) -> TemplateWords:
        ...

    @classmethod
    @property
    @abstractmethod
    def opts(cls) -> List[Opt]:
        ...

    # these fields are automatically initialised during inheritance (__init_subclass__)
    _opts_postprocess: List[Tuple[TemplateOpts, Callable]]
    _opts_alias_mapping: Dict[str, Opt]
    _opts_name_mapping: Dict[str, Opt]

    # TODO: add property type checking
    def __init_subclass__(cls):
        super().__init_subclass__()

        cls._opts_alias_mapping = dict()
        # false inspection warning for property
        # noinspection PyTypeChecker
        for opt in cls.opts:
            for alias in opt.aliases:
                cls._opts_alias_mapping[alias] = opt

        # false inspection warning for property
        # noinspection PyTypeChecker
        cls._opts_name_mapping = {opt.name: opt for opt in cls.opts}

        def pp_func_predicate(pp_func):
            return inspect.ismethod(pp_func) and hasattr(pp_func, _OPTS_POSTPROCESS_ATTR_KEY)

        # inspect all opt postprocessing functions
        pp_funcs = [m[1] for m in inspect.getmembers(cls, predicate=pp_func_predicate)]

        cls._opts_postprocess = list()
        for func in pp_funcs:
            _, tmpl_opts = cls._extract(getattr(func, _OPTS_POSTPROCESS_ATTR_KEY))
            assert tmpl_opts is not None
            cls._opts_postprocess.append((tmpl_opts, func))

    @classmethod
    def check_entry(cls, cmd: Union[CommandWords, TemplateWords]) \
            -> bool:
        # noinspection PyTypeChecker
        matcher = TemplateMatcher(tmpl=cls.entry)
        match = matcher.full_match(cmd)

        if match is None:
            return False
        return True

    @classmethod
    def extract_command_call(cls, cmd: CommandWords) \
            -> Tuple[Optional[CommandWords],
                     Optional[CommandOpts]]:
        if not cls.check_entry(cmd):
            return None, None

        return cls._extract(cmd)

    @classmethod
    def extract_command_template(cls, tmpl: TemplateWords) \
            -> Tuple[Optional[TemplateWords],
                     Optional[TemplateOpts]]:
        if not cls.check_entry(tmpl):
            return None, None

        return cls._extract(tmpl)

    @classmethod
    def _extract(cls, cmd: Union[CommandWords, TemplateWords]) \
            -> Union[
                Tuple[Optional[CommandWords], Optional[CommandOpts]],
                Tuple[Optional[TemplateWords], Optional[TemplateOpts]]
            ]:
        opts_extractor = OptsExtractor(opts_map=cls._opts_alias_mapping)
        tmp = copy.deepcopy(cmd)
        return opts_extractor.extract(tmp)

    @classmethod
    def postprocess_command_opts(cls, cmd_opts: CommandOpts, tweaks: TemplateTweaks) \
            -> Tuple[Dict[str, Any], CommandOpts]:
        module_params = dict()
        unmatched_opts = {k: listify(v) for k, v in cmd_opts.items()}

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
    RegistryEntry = Tuple[str, Type[CommandConfigABC]]

    configurations: Dict[str, Type[CommandConfigABC]]
    config_cache: Dict[str, List[RegistryEntry]]

    def __init__(self):
        self.configurations = dict()
        self.config_cache = dict()

    def add_entry(self, cmd_name: str, config_cls: Type[CommandConfigABC]) \
            -> None:
        assert cmd_name not in self.configurations
        self.configurations[cmd_name] = config_cls

        first_part: TemplatePart = config_cls.entry[0]
        # in order for new config to be cached
        # the first part from command's 'entry' should be a constant string
        assert not first_part.parts
        if first_part.value not in self.config_cache:
            self.config_cache[first_part.value] = list()
        self.config_cache[first_part.value].append((cmd_name, config_cls))

    def fetch_by_command(self, cmd: CommandWords) \
            -> List[RegistryEntry]:
        # ignoring commands that have parameter in first word
        if cmd[0].parts:
            return []
        return self.config_cache.get(cmd[0].value, [])

    def fetch_by_name(self, command_name: str) \
            -> Optional[RegistryEntry]:
        return self.configurations.get(command_name, None)


global_command_config_entry = CommandConfigRegistry()


def postprocess_opts(tmpl_str: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        tmpl = tmpl_s(tmpl_str)
        assert tmpl is not None

        # attribute is later used to identify opt postprocessing methods
        # and create corresponding command opt template
        setattr(func, _OPTS_POSTPROCESS_ATTR_KEY, tmpl)

        # TODO: check function return value
        # TODO: check if func accepts argument 'tweaks'
        # TODO: check if other arguments of func correspond
        #  to fields from template and have desired type (list or str)
        return func

    return decorator


def command_config(cmd_name: str):
    def decorator(cls):
        global_command_config_entry.add_entry(cmd_name=cmd_name, config_cls=cls)
        return cls

    return decorator
