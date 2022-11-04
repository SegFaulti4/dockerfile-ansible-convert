import logging

from sandbox.shell_parser.main import SandboxShellParser
from sandbox.dockerfile_parser.main import SandboxDockerfileParser
from sandbox.task_matcher.main import SandboxTaskMatcher
from src.ansible_generator.main import RoleGenerator as SandboxRoleGenerator
import sandbox.utils.file_utils as file_utils

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()
    dockerfile_parser = SandboxDockerfileParser(shell_parser=shell_parser)
    task_matcher = SandboxTaskMatcher()

    PRINT_PATH = True
    PRINT_SOURCE = True
    PRINT_DOCKERFILE_PARSER = True
    PRINT_ROLE_GENERATOR = True

    with open("./input", "r") as inF:
        for name in inF.readlines():
            path = f"{file_utils.DOCKERFILES_DIR}/{name.strip()}"
            if PRINT_PATH:
                print('########')
                print("# PATH #")
                print('########')
                print()
                print(path)
                print()

            with open(path, "r") as df:
                source = "".join(df.readlines())

            if PRINT_SOURCE:
                print('##########')
                print("# SOURCE #")
                print('##########')
                print()
                print(source)

            content = dockerfile_parser.from_str(source)
            if PRINT_DOCKERFILE_PARSER:
                print('#####################')
                print("# DOCKERFILE PARSER #")
                print('#####################')
                print()
                for obj in content.directives:
                    print(f"{obj}")
                print()

            role = SandboxRoleGenerator(tm=task_matcher, dc=content).generate()
            if PRINT_ROLE_GENERATOR:
                print('##################')
                print("# ROLE GENERATOR #")
                print('##################')
                print()
                print(role)
                print()
