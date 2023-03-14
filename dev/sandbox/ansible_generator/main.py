import logging
import oyaml as yaml
import sys
import os.path

from dev.sandbox.shell.main import SandboxShellParser
from dev.sandbox.containerfile.main import SandboxDockerfileParser
from dev.sandbox.ansible_matcher.main import SandboxTaskMatcher
from src.containerfile.main import *
from src.ansible_generator.main import RoleGenerator as SandboxRoleGenerator
import dev.utils.data_utils as data_utils

from src.log import globalLog


def print_header(s):
    print(f"\033[4m\033[97m{s}\033[0m\033[0m")


if __name__ == "__main__":
    globalLog.setLevel(logging.DEBUG)
    shell_parser = SandboxShellParser()
    dockerfile_parser = SandboxDockerfileParser(shell_parser=shell_parser)
    task_matcher = SandboxTaskMatcher()

    FILES_DIR = data_utils.UBUNTU_FILES_DIR
    SHOW_PATH = True
    SHOW_SOURCE = True
    SHOW_DOCKERFILE_PARSER = True
    SHOW_ROLE_GENERATOR = True

    with open("input", "r") as inF:
        for name in inF.readlines():
            path = os.path.join(FILES_DIR, name.strip())

            with open(path, "r") as df:
                source = "".join(df.readlines())

            content = dockerfile_parser.from_str(source)
            tasks = SandboxRoleGenerator(tm=task_matcher, dc=content).generate()

            if SHOW_PATH:
                print_header("PATH:")
                print(f"{path}\n")
            if SHOW_SOURCE:
                print_header("SOURCE:")
                print(f"{source.strip()}\n")
            if SHOW_DOCKERFILE_PARSER:
                rep = "\n".join(str(obj) for obj in content.directives)
                print_header("DOCKERFILE PARSER:")
                print(f"{rep}\n")
            if SHOW_ROLE_GENERATOR:
                print_header("ROLE GENERATOR:")
                yaml.safe_dump(tasks, sys.stdout)
                print()
