import logging
import csv
import os
import multiprocessing
import subprocess
from collections import defaultdict
from tabulate import tabulate

from src.ansible_generator.main import *
from src.ansible_generator.statistics import *
from src.ansible_matcher.main import *
from src.ansible_matcher.statistics import *
from src.containerfile.tpdockerfile.main import *
from src.shell.bashlex.main import *
from dev.utils.data_utils import *


def gen_matcher_tests(dockerfile_parser: DockerfileParser, task_matcher: TaskMatcher):
    matcher_tests = []

    filenames = filenames_from_dir(CONTAINERFILES_DIR)
    for name in tqdm(filenames[:16], desc="Collecting tests"):
        path = os.path.join(CONTAINERFILES_DIR, name)
        try:
            with open(path.strip(), "r") as df:
                source = "".join(df.readlines())

            content = dockerfile_parser.from_str(source)
            generator = RoleGenerator(tm=task_matcher, dc=content, collect_matcher_tests=True)
            generator.generate()
            matcher_tests.extend(generator.matcher_tests)

        except Exception as exc:
            globalLog.warning(type(exc), exc)

    matcher_tests = list(set(matcher_tests))

    with open(os.path.join(DATA_DIR, "tests"), "w") as outF:
        outF.writelines(m + "\n" for m in matcher_tests)
    return matcher_tests


def test_container_run(test: str, idx: int):
    name = f"deb-test-{idx}"
    command = f'docker run --name={name} debian-test bash -c "{test}" > /dev/null && docker inspect {name} --format="{{{{.State.ExitCode}}}}" && docker rm {name} > /dev/null'
    print(command)
    result = subprocess.run(['/bin/bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)
    print('\033[91m' + result.stderr + '\033[0m')


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)

    shell_parser = BashlexShellParser()
    dockerfile_parser = TPDockerfileParser(shell_parser=shell_parser)
    task_matcher = TaskMatcher()

    tests = gen_matcher_tests(dockerfile_parser, task_matcher)
    # with multiprocessing.Pool() as pool:
    test_container_run(tests[1], 2)
