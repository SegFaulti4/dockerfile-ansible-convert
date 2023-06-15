from src.ansible_matcher.commands.command_config import *


@command_config("pip")
class PipConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("pip <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        []
