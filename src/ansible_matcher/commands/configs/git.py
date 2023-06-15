from src.ansible_matcher.commands.command_config import *


@command_config("git")
class GitConfig(CommandConfigABC):
    entry: ClassVar[CommandTemplateParts] = tmpl_c("git <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        []
