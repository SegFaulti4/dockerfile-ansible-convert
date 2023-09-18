from src.ansible_matcher.commands.command_config import *


@command_config("cd")
class CdConfig(CommandConfigABC):
    entry: ClassVar[TemplateWords] = tmpl_s("cd <<parameters : m>>")
    opts: ClassVar[List[Opt]] = \
        [
            Opt("links", False, False,
                ['-L']),

            Opt("physical", False, False,
                ['-P']),

            Opt("exit", False, False,
                ['-e']),

            Opt("extended", False, False,
                ['-@'])
        ]
