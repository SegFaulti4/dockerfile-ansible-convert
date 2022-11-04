import logging
import dockerfile

from src.dockerfile.main import *
from sandbox.shell_parser.main import SandboxShellParser
from src.dockerfile.tpdockerfile.main import TPDockerfileParser as SandboxDockerfileParser
import sandbox.utils.file_utils as file_utils

from log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()
    dockerfile_parser = SandboxDockerfileParser(shell_parser=shell_parser)

    PRINT_PATH = True
    PRINT_SOURCE = True
    PRINT_DOCKERFILE = True
    PRINT_DOCKERFILE_PARSER = True

    with open("./input", "r") as inF:
        for name in inF.readlines():
            try:
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

                if PRINT_DOCKERFILE:
                    objs = dockerfile.parse_string(source)
                    print('##############')
                    print("# DOCKERFILE #")
                    print('##############')
                    print()
                    for obj in objs:
                        print(f"{obj}")
                    print()

                if PRINT_DOCKERFILE_PARSER:
                    content = dockerfile_parser.from_str(source)
                    print('#####################')
                    print("# CONTENT GENERATOR #")
                    print('#####################')
                    print()
                    for obj in content.directives:
                        print(f"{obj}")
                    print()

            except Exception as exc:
                print(f"{type(exc)}: {exc}")
                print()
