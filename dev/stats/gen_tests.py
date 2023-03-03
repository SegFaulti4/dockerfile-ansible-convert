import logging
import parts
import multiprocessing
import subprocess
from subprocess import PIPE
from typing import Iterable

from src.ansible_generator.main import *
from src.ansible_matcher.main import *
from src.containerfile.tpdockerfile.main import *
from src.shell.bashlex.main import *
from dev.utils.data_utils import *


def collect_matcher_tests(dockerfile_parser: DockerfileParser, task_matcher: TaskMatcher):
    tests = []

    filenames = filenames_from_dir(CONTAINERFILES_DIR)
    for name in tqdm(filenames[:16], desc="Collecting matcher_tests"):
        path = os.path.join(CONTAINERFILES_DIR, name)
        try:
            with open(path.strip(), "r") as df:
                source = "".join(df.readlines())

            content = dockerfile_parser.from_str(source)
            generator = RoleGenerator(tm=task_matcher, dc=content, collect_matcher_tests=True)
            generator.generate()
            tests.extend(generator.matcher_tests)

        except Exception as exc:
            globalLog.warning(type(exc), exc)

    tests = list(dict.fromkeys(tests))
    return tests


def container_run_matcher_tests(args: Tuple[List[str], Iterable[int]]) -> List[str]:
    tests, span = args
    good_runs = []

    for idx in span:
        test = tests[idx]
        container_name = f"deb-test-{idx}"

        run_comm = f'docker run --name={container_name} ubuntu-test bash -c "{test}"'
        inspect_comm = f'docker inspect {container_name} --format="{{{{.State.ExitCode}}}}"'
        rm_comm = f'docker rm {container_name}'

        try:
            run_result = subprocess.run(['/bin/bash', '-c', run_comm],
                                        stdout=PIPE, stderr=PIPE, text=True, timeout=120)
            inspect_result = subprocess.run(['/bin/bash', '-c', inspect_comm], stdout=PIPE, stderr=PIPE, text=True)
            if not inspect_result.stderr and inspect_result.stdout.strip() == "0":
                success = True
            else:
                success = False

            stdo = run_result.stdout
            stde = run_result.stderr
        except subprocess.TimeoutExpired:
            success = False
            stdo = ""
            stde = "Time limit exceeded"

        if success:
            good_runs.append(test)

        print(run_comm)
        print(success)
        # print(stdo)
        # print(stde)
        print()

        subprocess.run(['/bin/bash', '-c', rm_comm], stdout=PIPE, stderr=PIPE, text=True)

    return good_runs


if __name__ == "__main__":
    globalLog.setLevel(logging.WARNING)

    shell_parser = BashlexShellParser()
    dockerfile_parser = TPDockerfileParser(shell_parser=shell_parser)
    task_matcher = TaskMatcher()

    matcher_tests = collect_matcher_tests(dockerfile_parser, task_matcher)

    n_proc = 6
    with multiprocessing.Pool(processes=n_proc) as pool:
        spans = parts.parts(range(len(matcher_tests)), n_proc)

        per_proc = pool.map(container_run_matcher_tests, [(matcher_tests, span) for span in spans])
        good_runs = [good_run for p in per_proc for good_run in p]

    print(good_runs)

    with open(os.path.join(DATA_DIR, "matcher_tests"), "w") as outF:
        outF.writelines(t + "\n" for t in good_runs)
