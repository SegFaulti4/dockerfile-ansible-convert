from src.ansible_matcher.commands.command_config import *


@command_config("pip")
class PipConfig(CommandConfigABC):
    entry: ClassVar[TemplateWords] = tmpl_s("pip <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        []
