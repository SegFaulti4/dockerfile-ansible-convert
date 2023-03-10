import logging

from src.ansible_matcher.main import *
from dev.sandbox.shell.main import SandboxShellParser
from src.ansible_matcher.main import TaskMatcher as SandboxTaskMatcher

from src.log import globalLog


def print_header(s):
    print(f"\033[4m\033[97m{s}\033[0m\033[0m")


if __name__ == "__main__":
    globalLog.setLevel(logging.DEBUG)
    shell_parser = SandboxShellParser()
    task_matcher = SandboxTaskMatcher()
    cwd = "/"
    usr = "root"

    SHOW_SOURCE = True
    SHOW_SHELL_PARSER = True
    SHOW_TASK_MATCHER = True

    INPUT_PATH = "./input"

    with open(INPUT_PATH, "r") as inF:
        for line in inF.readlines():
            line = line.strip()
            if not line:
                continue

            try:
                script = shell_parser.parse_as_script(line)
                comm = script.parts[0]
                if isinstance(comm, ShellCommandObject):
                    ext = task_matcher.extract_command(comm.parts)
                    obj = task_matcher.match_command(comm.parts, cwd=cwd, usr=usr)
                else:
                    obj = None

                if SHOW_SOURCE:
                    print_header("SOURCE:")
                    print(f"{line}\n")
                if SHOW_SHELL_PARSER:
                    print_header("SHELL_PARSER:")
                    print(f"{comm}\n")
                if SHOW_TASK_MATCHER:
                    print_header("TASK MATCHER:")
                    print(f"{obj}\n")
                print(f"{ext}\n")

            except IOError as exc:
                print(f"{type(exc)}: {exc}")
                print()
