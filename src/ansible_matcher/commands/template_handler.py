from typing import Optional, Any, Union, Tuple, List, Dict, Callable

from src.ansible_matcher.template_lang import TemplatePart, CommandTemplateParts, CommandCallParts, TemplateTweaks, tmpl_c


AnsibleTasks = List[Dict[str, Any]]

_TEMPLATE_HANDLER_ATTR_KEY = '_postprocess_configs'


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


def template_handler(tmpl_s: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        tmpl = tmpl_c(tmpl_s)
        assert tmpl is not None
        global_template_handler_registry.add_entry(command_template=tmpl, tmpl_handler=func)
        return func

    return decorator


def postprocess_commands(*args: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        setattr(func, _TEMPLATE_HANDLER_ATTR_KEY, list(args))
        return func

    return decorator
