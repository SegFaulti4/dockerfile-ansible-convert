import logging

from log import globalLog
from dockerfile_ansible_convert import bash_parse
from dockerfile_ansible_convert import module_match
from dockerfile_ansible_convert import generator

with open("../data/mined", "r") as inF:
    globalLog.setLevel(logging.WARNING)

    for line in inF.readlines():
        for command in bash_parse.parse_bash_commands(line):
            if isinstance(command, bash_parse.CommandNode) and command.name is not None and command.name == "apt-get":
                match = module_match.ModuleMatcher.match(generator.PlaybookContext(), command)
                globalLog.warning("from:")
                globalLog.warning(command)
                if match is not None:
                    globalLog.warning("to:")
                    globalLog.warning(match)

