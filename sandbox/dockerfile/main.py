import logging
import dockerfile

from src.dockerfile.main import *
from sandbox.shell.main import SandboxShellParser
from src.dockerfile.tpdockerfile.main import TPDockerfileContentGenerator as SandboxDockerfileContentGenerator

from log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()
    content_generator = SandboxDockerfileContentGenerator(shell_parser=shell_parser)

    PRINT_PATH = True
    PRINT_SOURCE = True
    PRINT_DOCKERFILE = True
    PRINT_CONTENT_GENERATOR = True

    with open("./data", "r") as inF:
        for line in inF.readlines():
            try:
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

                if PRINT_DOCKERFILE:
                    objs = dockerfile.parse_string(source)
                    print('##############')
                    print("# DOCKERFILE #")
                    print('##############')
                    print()
                    for obj in objs:
                        print(f"{obj}")
                    print()

                if PRINT_CONTENT_GENERATOR:
                    content = content_generator.from_str(source)
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
