import logging
import oyaml as yaml
import sys

from dev.sandbox.shell.main import SandboxShellParser
from dev.sandbox.containerfile.main import SandboxDockerfileParser
from dev.sandbox.ansible_matcher.main import SandboxTaskMatcher
from src.ansible_generator.main import RoleGenerator as SandboxRoleGenerator
import dev.sandbox.utils.file_utils as file_utils

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.DEBUG)
    shell_parser = SandboxShellParser()
    dockerfile_parser = SandboxDockerfileParser(shell_parser=shell_parser)
    task_matcher = SandboxTaskMatcher()

    SHOW_PATH = True
    SHOW_SOURCE = True
    SHOW_DOCKERFILE_PARSER = True
    SHOW_ROLE_GENERATOR = True

    with open("input", "r") as inF:
        for name in inF.readlines():
            path = f"{file_utils.DOCKERFILES_DIR}{name.strip()}"

            with open(path, "r") as df:
                source = "".join(df.readlines())

            content = dockerfile_parser.from_str(source)
            tasks = SandboxRoleGenerator(tm=task_matcher, dc=content).generate()

            if SHOW_PATH:
                print(f"PATH:\t{path}\n")
            if SHOW_SOURCE:
                print(f"SOURCE:\n{source}\n")
            if SHOW_DOCKERFILE_PARSER:
                rep = "\n".join(str(obj) for obj in content.directives)
                print(f"DOCKERFILE PARSER:\n{rep}\n")
            if SHOW_ROLE_GENERATOR:
                print("ROLE GENERATOR:\n")
                yaml.dump(tasks, sys.stdout)
                print()
