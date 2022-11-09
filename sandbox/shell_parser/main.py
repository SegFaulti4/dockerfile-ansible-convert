import logging
import bashlex

from src.shell.bashlex.main import BashlexShellParser as SandboxShellParser

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()

    PRINT_SOURCE = True
    PRINT_BASHLEX = True
    PRINT_SHELL_PARSER = True

    with open("./input", "r") as inF:
        for line in inF.readlines():
            try:
                if PRINT_SOURCE:
                    print('##########')
                    print("# SOURCE #")
                    print('##########')
                    print()
                    print(line.strip())
                    print()

                if PRINT_BASHLEX:
                    objs = bashlex.parse(line)
                    print('###########')
                    print("# BASHLEX #")
                    print('###########')
                    print()
                    for obj in objs:
                        print(f"{obj}")
                    print()

                if PRINT_SHELL_PARSER:
                    objs = shell_parser.parse(line)
                    print('################')
                    print("# SHELL PARSER #")
                    print('################')
                    print()
                    for obj in objs:
                        print(f"{obj}")
                    print()

            except Exception as exc:
                print(f"{type(exc)}: {exc}")
                print()
