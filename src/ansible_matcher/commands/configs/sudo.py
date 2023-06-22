from src.ansible_matcher.commands.command_config import *


@command_config("sudo")
class SudoConfig(CommandConfigABC):
    entry: ClassVar[TemplateWords] = tmpl_s("sudo <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        []
