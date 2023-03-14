import logging

from dev.sandbox.shell.main import SandboxShellParser
from dev.sandbox.containerfile.main import SandboxDockerfileParser
from dev.sandbox.ansible_matcher.main import SandboxTaskMatcher
from dev.sandbox.ansible_generator.main import SandboxRoleGenerator
from dev.utils.data_utils import *
import dev.sandbox.utils.ansible_utils as ansible_utils
import dev.sandbox.utils.cloud_utils as cloud_utils

from src.log import globalLog


if __name__ == "__main__":
    globalLog.setLevel(logging.INFO)
    shell_parser = SandboxShellParser()
    dockerfile_parser = SandboxDockerfileParser(shell_parser=shell_parser)
    task_matcher = SandboxTaskMatcher()

    FILES_DIR = UBUNTU_FILES_DIR
    PRINT_PATH = True
    PRINT_SOURCE = True
    PRINT_DOCKERFILE_PARSER = True
    PRINT_ROLE_GENERATOR = True
    EXECUTE_ROLE = False

    for name, path in zip(filenames_from_dir(FILES_DIR), filepaths_from_dir(FILES_DIR)):
        if PRINT_PATH:
            print('########')
            print("# PATH #")
            print('########')
            print()
            print(path.strip())
            print()

        with open(path.strip(), "r") as df:
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

        tasks = SandboxRoleGenerator(tm=task_matcher, dc=content).generate()
        if PRINT_ROLE_GENERATOR:
            print('##################')
            print("# ROLE GENERATOR #")
            print('##################')
            print()
            print(tasks)
            print()

        role_name = name[:name.find('.')] if '.' in name else name
        ansible_utils.write_new_role(role_name=role_name, tasks=tasks)
        if EXECUTE_ROLE:
            print('################')
            print("# EXECUTE ROLE #")
            print('################')
            print()
            host_ip, ansible_ssh_user = cloud_utils.setup_instance()
            ansible_utils.execute_role(role_name=role_name, host_ip=host_ip,
                                       ansible_ssh_user=ansible_ssh_user)
