from src.ansible_matcher.commands.command_config import *


@command_config("set")
class SetConfig(CommandConfigABC):
    entry: ClassVar[TemplateWords] = tmpl_s("set <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        []
