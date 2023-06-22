from typing import Optional, Any, Tuple, List, Dict, Callable

from src.ansible_matcher.template_lang.main import \
    TemplatePart, TemplateWords, CommandWords, TemplateTweaks, tmpl_s


AnsibleTasks = List[Dict[str, Any]]

_TEMPLATE_HANDLER_POSTPROCESS_COMMANDS_ATTR = '_postprocess_configs'
_TEMPLATE_HANDLER_PASS_OPTS_ATTR = '_pass_command_opts'


# TODO: add command template extraction for registered handlers
class TemplateHandlerRegistry:
    templates: List[Tuple[TemplateWords, Callable]]
    template_cache: Dict[str, List[Tuple[TemplateWords, Callable]]]

    def __init__(self):
        self.templates = list()
        self.template_cache = dict()

    def add_entry(self, command_template: TemplateWords, tmpl_handler: Callable) \
            -> None:
        self.templates.append((command_template, tmpl_handler))

        first_part: TemplatePart = command_template[0]
        # in order for new template to be cached
        # the first template part should be a constant string
        assert not first_part.parts
        if first_part.value not in self.template_cache:
            self.template_cache[first_part.value] = list()
        self.template_cache[first_part.value].append((command_template, tmpl_handler))

    def fetch_by_command(self, comm: CommandWords) \
            -> List[Tuple[TemplateWords, Callable, List[str], bool]]:
        if comm[0].parts:
            return []
        cached = self.template_cache.get(comm[0].value, [])
        res = []
        for tmpl, handler_func in cached:
            postprocess_configs = getattr(handler_func, _TEMPLATE_HANDLER_POSTPROCESS_COMMANDS_ATTR, [])
            pass_opts = getattr(handler_func, _TEMPLATE_HANDLER_PASS_OPTS_ATTR, False)
            res.append((tmpl, handler_func, postprocess_configs, pass_opts))
        return res


global_template_handler_registry = TemplateHandlerRegistry()


def template_handler(tmpl_str: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        tmpl = tmpl_s(tmpl_str)
        assert tmpl is not None
        global_template_handler_registry.add_entry(command_template=tmpl, tmpl_handler=func)

        # TODO: check function return value type
        # TODO: check if func accepts argument 'tweaks'
        # TODO: check if other arguments of func correspond
        #  to fields from template and have desired type (list or str)
        return func

    return decorator


# TODO: change args type to type[CommandConfig]
# all handler modules then will need to import required command configs themselves
def postprocess_commands(*args: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        setattr(func, _TEMPLATE_HANDLER_POSTPROCESS_COMMANDS_ATTR, list(args))
        return func

    return decorator


# TODO: check that function accepts argument `opts: CommandCallOpts`
def pass_command_opts(func: Callable) -> Callable:
    setattr(func, _TEMPLATE_HANDLER_PASS_OPTS_ATTR, True)
    return func
