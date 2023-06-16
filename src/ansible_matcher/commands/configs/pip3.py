from src.ansible_matcher.commands.command_config import *


@command_config("pip3")
class Pip3Config(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("pip3 <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        []
