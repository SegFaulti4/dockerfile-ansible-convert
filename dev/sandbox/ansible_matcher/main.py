import logging

from src.ansible_matcher.main import *
from dev.sandbox.shell.main import SandboxShellParser
from src.ansible_matcher.example_based.main import ExampleBasedMatcher as SandboxTaskMatcher

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.WARNING)
    shell_parser = SandboxShellParser()
    task_matcher = SandboxTaskMatcher()

    SHOW_SOURCE = False
    SHOW_SHELL_PARSER = False
    SHOW_TASK_MATCHER = False

    INPUT_PATH = "./input"

    with open(INPUT_PATH, "r") as inF:
        for line in inF.readlines():
            line = line.strip()
            if not line:
                continue

            try:
                shell_objs = shell_parser.parse(line)
                objs = [task_matcher.match_command(obj.parts) for obj in shell_objs if isinstance(obj, ShellCommandObject)]

                if SHOW_SOURCE:
                    print(f"SOURCE:\n\t{line}\n")
                if SHOW_SHELL_PARSER:
                    rep = "\n".join(str(obj) for obj in shell_objs)
                    print(f"SHELL PARSER:\n{rep}\n")
                if SHOW_TASK_MATCHER:
                    rep = "\n".join(str(obj) for obj in objs)
                    print(f"TASK MATCHER:\n{rep}\n")

            except IOError as exc:
                print(f"{type(exc)}: {exc}")
                print()
