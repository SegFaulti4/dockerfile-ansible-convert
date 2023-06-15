import inspect
import copy
from abc import ABC, abstractmethod
from typing import Optional, Any, Union, Tuple, List, Dict, Callable, ClassVar

from src.ansible_matcher.template_lang import CommandTemplateMatcher, \
    CommandCallParts, CommandTemplateParts, TemplatePart, TemplateTweaks, tmpl_c
from src.ansible_matcher.command_extraction import Opt, CommandCallOpts, CommandTemplateOpts, \
    ExtractedCommandCall, ExtractedCommandTemplate, CommandOptsExtractor, match_extracted_call_opts
from src.ansible_matcher.utils import *


_OPTS_POSTPROCESS_ATTR_KEY = "_opts_tmpl"


class CommandConfigABC(ABC):

    # entry: ClassVar[CommandTemplateParts] = NotImplemented

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

    # TODO: add property type checking
    def __init_subclass__(cls):
        super().__init_subclass__()

        cls._opts_alias_mapping = dict()
        # false inspection warning for property
        # noinspection PyTypeChecker
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
        # noinspection PyTypeChecker
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
    RegistryEntry = Tuple[str, Type[CommandConfigABC]]

    configurations: Dict[str, Type[CommandConfigABC]]
    config_cache: Dict[str, List[RegistryEntry]]

    def __init__(self):
        self.configurations = dict()
        self.config_cache = dict()

    def add_entry(self, command_name: str, config_cls: Type[CommandConfigABC]) -> None:
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
        tmpl = tmpl_c(tmpl_s)
        assert tmpl is not None

        # attribute is later used to identify opt postprocessing methods
        # and create corresponding command opt template
        setattr(func, _OPTS_POSTPROCESS_ATTR_KEY, tmpl)

        # TODO: check if func accepts argument 'tweaks'
        # TODO: check if other arguments of func correspond
        #  to fields from template and have desired type (list or str)
        return func

    return decorator


def command_config(command_name: str):
    def decorator(cls):
        global_command_config_entry.add_entry(command_name=command_name, config_cls=cls)
        return cls

    return decorator
