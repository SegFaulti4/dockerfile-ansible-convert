import logging

from src.ansible_generator.main import *
from sandbox.shell.main import SandboxShellParser
from sandbox.dockerfile.main import SandboxDockerfileContentGenerator
from sandbox.ansible_matcher.main import SandboxTaskMatcher
from src.ansible_generator.main import RoleGenerator as SandboxRoleGenerator

from log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()
    content_generator = SandboxDockerfileContentGenerator(shell_parser=shell_parser)
    task_matcher = SandboxTaskMatcher()

    PRINT_PATH = True
    PRINT_SOURCE = True
    PRINT_CONTENT_GENERATOR = True
    PRINT_ROLE_GENERATOR = True

    with open("./data", "r") as inF:
        for line in inF.readlines():
            if PRINT_PATH:
                print('########')
                print("# PATH #")
                print('########')
                print()
                print(line.strip())
                print()

            with open(line.strip(), "r") as df:
                source = "".join(df.readlines())

            if PRINT_SOURCE:
                print('##########')
                print("# SOURCE #")
                print('##########')
                print()
                print(source)

            content = content_generator.from_str(source)
            if PRINT_CONTENT_GENERATOR:
                print('#####################')
                print("# CONTENT GENERATOR #")
                print('#####################')
                print()
                for obj in content.directives:
                    print(f"{obj}")
                print()

            role_generator = SandboxRoleGenerator(tm=task_matcher, dc=content)
            if PRINT_ROLE_GENERATOR:
                print('##################')
                print("# ROLE GENERATOR #")
                print('##################')
                print()
                role = role_generator.generate()
                print(role)
                print()
