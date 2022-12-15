import logging

from src.ansible_matcher.main import *
from sandbox.shell_parser.main import SandboxShellParser
from src.ansible_matcher.example_based.main import ExampleBasedMatcher as SandboxTaskMatcher

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()
    task_matcher = SandboxTaskMatcher()

    PRINT_SOURCE = True
    PRINT_SHELL_PARSER = True
    PRINT_TASK_MATCHER = True

    with open("./input", "r") as inF:
        for line in inF.readlines():
            line = line.strip()
            if not line:
                continue

            try:
                if PRINT_SOURCE:
                    print('##########')
                    print("# SOURCE #")
                    print('##########')
                    print()
                    print(line)
                    print()

                shell_objs = shell_parser.parse(line)
                if PRINT_SHELL_PARSER:
                    print('################')
                    print("# SHELL PARSER #")
                    print('################')
                    print()
                    for obj in shell_objs:
                        print(f"{obj}")
                    print()

                if PRINT_TASK_MATCHER:
                    print('################')
                    print("# TASK MATCHER #")
                    print('################')
                    print()
                    for obj in shell_objs:
                        if isinstance(obj, ShellCommandObject):
                            task = task_matcher.match_command(obj.parts)
                            print(f"{task}")
                    print()

            except IOError as exc:
                print(f"{type(exc)}: {exc}")
                print()