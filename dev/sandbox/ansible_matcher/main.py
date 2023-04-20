import logging
import yaml

from src.ansible_matcher.main import *
from dev.sandbox.shell.main import SandboxShellParser
from src.ansible_matcher.main import TaskMatcher as SandboxTaskMatcher

from src.log import globalLog


def print_header(s):
    print(f"\033[4m\033[97m{s}\033[0m\033[0m")


class MyDumper(yaml.Dumper):
    # HACK: insert blank lines between top-level objects
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


# some black magic - https://stackoverflow.com/a/40044739
def represent_str(self, data):
    tag = u'tag:yaml.org,2002:str'
    style = None
    if '{{' in data and '}}' in data or "'" in data:
        style = '"'
    return self.represent_scalar(tag, data, style=style)


if __name__ == "__main__":
    yaml.add_representer(str, represent_str)

    globalLog.setLevel(logging.INFO)
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
                    s = "---\n" + yaml.dump(obj, sort_keys=False, Dumper=MyDumper,
                                            default_flow_style=False, explicit_start=False,
                                            canonical=False, width=1000000000)
                    print(f"{s}\n")
                print(f"{ext}\n")

            except IOError as exc:
                print(f"{type(exc)}: {exc}")
                print()
