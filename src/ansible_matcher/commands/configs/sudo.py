from src.ansible_matcher.commands.command_config import *


@command_config("sudo")
class SudoConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("sudo <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        []
