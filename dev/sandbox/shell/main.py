import logging
import bashlex

from src.shell.main import *
from src.shell.bashlex.main import BashlexShellParser as SandboxShellParser

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()

    SHOW_SOURCE = True
    SHOW_BASHLEX = True
    SHOW_SHELL_PARSER = True

    SAVE_COMMANDS = True
    SAVE_COMMANDS_PATH = "commands"
    commands = []

    INPUT_PATH = "./input.txt"

    with open(INPUT_PATH, "r") as inF:
        for line in inF.readlines():
            line = line.strip()
            if not line:
                continue

            try:
                bashlex_objs = bashlex.parse(line)
                objs = shell_parser.parse(line)

                if SHOW_SOURCE:
                    print(f"SOURCE:\n\t{line}\n")
                if SHOW_BASHLEX:
                    rep = "\n".join(str(obj) for obj in bashlex_objs)
                    print(f"BASHLEX:\n{rep}\n")
                if SHOW_SHELL_PARSER:
                    rep = "\n".join(str(obj) for obj in objs)
                    print(f"SHELL PARSER:\n{rep}\n")

                if SAVE_COMMANDS:
                    commands.extend(filter(lambda x: isinstance(x, ShellCommandObject), objs))

            except Exception as exc:
                print(f"{type(exc)}: {exc}")
                print()

    if SAVE_COMMANDS:
        with open(SAVE_COMMANDS_PATH, "w") as outF:
            for comm in commands:
                outF.write(comm.line + "\n")
