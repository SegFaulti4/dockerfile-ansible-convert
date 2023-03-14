import logging
import dockerfile
import os.path

from dev.sandbox.shell.main import SandboxShellParser
from src.containerfile.tpdockerfile.main import TPDockerfileParser as SandboxDockerfileParser
import dev.utils.data_utils as data_utils

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()
    dockerfile_parser = SandboxDockerfileParser(shell_parser=shell_parser)

    FILES_DIR = data_utils.UBUNTU_FILES_DIR
    SHOW_PATH = True
    SHOW_SOURCE = True
    SHOW_DOCKERFILE = True
    SHOW_DOCKERFILE_PARSER = True

    with open("input", "r") as inF:
        for name in inF.readlines():
            try:
                path = os.path.join(FILES_DIR, name.strip())

                with open(path, "r") as df:
                    source = "".join(df.readlines())

                objs = dockerfile.parse_string(source)
                content = dockerfile_parser.from_str(source)

                if SHOW_PATH:
                    print(f"PATH:\t{path}\n")
                if SHOW_SOURCE:
                    print(f"SOURCE:\n{source}\n")
                if SHOW_DOCKERFILE:
                    rep = "\n".join(str(obj) for obj in objs)
                    print(f"DOCKERFILE:\n{rep}\n")
                if SHOW_DOCKERFILE_PARSER:
                    rep = "\n".join(str(obj) for obj in content.directives)
                    print(f"DOCKERFILE PARSER:\n{rep}\n")

            except Exception as exc:
                print(f"{type(exc)}: {exc}")
                print()
