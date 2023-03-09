import argparse
import sys
import yaml
import logging

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


def main():
    fh = logging.FileHandler('./log')
    fh.setLevel(logging.WARNING)
    globalLog.handlers.clear()
    globalLog.addHandler(fh)

    args = parse_arguments()
    dp = args.dockerfile
    out_s = open(args.output, 'w') if args.output else sys.stdout

    dockerfile_content = MainDockerfileParser(shell_parser=MainShellParser()).from_path(dp)
    tasks = MainRoleGenerator(dc=dockerfile_content, tm=MainTaskMatcher()).generate()

    yaml.dump(tasks, out_s)
