import argparse
import sys
import yaml
import logging
from typing import List, Dict, Any

from src.shell.bashlex.main import BashlexShellParser as MainShellParser
from src.containerfile.tpdockerfile.main import TPDockerfileParser as MainDockerfileParser
from src.ansible_matcher.main import TaskMatcher as MainTaskMatcher
from src.ansible_generator.main import RoleGenerator as MainRoleGenerator

from src.log import globalLog


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('dockerfile', action='store', help='Path to dockerfile')
    parser.add_argument('-o', '--output', action='store',
                        help='Path to resulting tasks file, if not provided stdout will be used')
    return parser.parse_args()


def represent_str(self, data):
    tag = u'tag:yaml.org,2002:str'
    style = None
    if '{{' in data and '}}' in data or "'" in data:
        style = '"'
    return self.represent_scalar(tag, data, style=style)


class TasksDumper(yaml.Dumper):

    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


def dump_tasks(tasks: List[Dict[str, Any]]) -> str:
    yaml.add_representer(str, represent_str)
    return "---\n" + yaml.dump(
        tasks,
        sort_keys=False,
        Dumper=TasksDumper,
        default_flow_style=False,
        explicit_start=False,
        canonical=False,
        width=1000000000
    )


def main():
    # fh = logging.FileHandler('./log')
    # fh.setLevel(logging.DEBUG)
    # globalLog.handlers.clear()
    # globalLog.addHandler(fh)
    globalLog.setLevel(logging.DEBUG)

    args = parse_arguments()
    dp = args.dockerfile
    out_s = open(args.output, 'w') if args.output else sys.stdout

    dockerfile_content = MainDockerfileParser(shell_parser=MainShellParser()).from_path(dp)
    tasks = MainRoleGenerator(dc=dockerfile_content, tm=MainTaskMatcher()).generate()

    s = dump_tasks(tasks)
    out_s.write(s)
    out_s.close()
