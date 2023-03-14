import logging
import parts
import multiprocessing
import subprocess
import time
# import p_tqdm
from subprocess import PIPE

from src.ansible_generator.main import *
from src.ansible_matcher.main import *
from src.containerfile.tpdockerfile.main import *
from src.shell.bashlex.main import *
from dev.utils.data_utils import *


def log_header(s: str) -> str:
    return f"{s.upper()}:"


def flag_print(*args, **kwargs):
    if "echo" in kwargs and kwargs["echo"]:
        del kwargs["echo"]
        print(*args, **kwargs)


def mine_matcher_tests(df_parser: DockerfileParser, task_matcher: TaskMatcher,
                       filepaths: List[str], tests_file: str, n_proc: int) -> List[str]:
    matcher_tests = []

    def worker(filepath: str) -> List[str]:
        try:
            with open(filepath.strip(), "r") as df:
                source = "".join(df.readlines())

            content = df_parser.from_str(source)
            generator = RoleGenerator(tm=task_matcher, dc=content, collect_matcher_tests=True)
            generator.generate()
            tests = generator.matcher_tests

        except Exception as exc:
            globalLog.info(type(exc), exc)
            tests = []

        return tests

    for path in tqdm(filepaths, desc="Collecting matcher tests", smoothing=1.0):
        matcher_tests.extend(worker(path))

    # matcher_tests = p_tqdm.p_map(worker, filenames, num_cpus=n_proc)
    matcher_tests = list(dict.fromkeys(matcher_tests))
    with open(tests_file, "w") as outF:
        outF.writelines(t + "\n" for t in matcher_tests)
    return matcher_tests


def read_matcher_tests(tests_file: str) -> List[str]:
    with open(tests_file, "r") as inF:
        tests = [line.strip() for line in inF]
    return tests


def filter_tests_worker(args: Tuple[List[str], int, bool, str]) -> List[str]:
    tests, idx, echo, log_dir = args
    filtered = []

    log_path = os.path.join(log_dir, f"filter-tests-{idx}")
    with open(log_path, "w") as logF:
        for test in tqdm(tests, desc=f"Filtering test set {idx}", smoothing=1.0):
            container_name = f"ubuntu-test-{idx}"
            run_comm = f'docker run --name={container_name} ubuntu-test-stand bash -c "{test}"'
            inspect_comm = f'docker inspect {container_name} --format="{{{{.State.ExitCode}}}}"'
            stop_rm_comm = f'docker stop {container_name} && docker rm {container_name}'

            try:
                flag_print(run_comm, echo=echo)
                run_result = subprocess.run(['/bin/bash', '-c', run_comm],
                                            stdout=PIPE, stderr=PIPE, text=True, timeout=120)
                flag_print(inspect_comm, echo=echo)
                inspect_result = subprocess.run(['/bin/bash', '-c', inspect_comm], stdout=PIPE, stderr=PIPE, text=True)

                success = True if not inspect_result.stderr and inspect_result.stdout.strip() == "0" else False
                run_stdout, run_stderr = run_result.stdout, run_result.stderr
            except subprocess.TimeoutExpired:
                success = False
                run_stdout, run_stderr = "", "Time limit exceeded"

            if success:
                filtered.append(test)
            logF.writelines([
                log_header("run command") + f"{run_comm}\n\n",
                log_header("run stdout") + f"{run_stdout}\n\n",
                log_header("run stderr") + f"{run_stderr}\n\n",
                log_header("success") + f"{success}\n\n"
            ])

            flag_print(stop_rm_comm, echo=echo)
            subprocess.run(['/bin/bash', '-c', stop_rm_comm], stdout=PIPE, stderr=PIPE, text=True)

    return filtered


def filter_matcher_tests(matcher_tests: List[str], n_proc: int, log_dir: str) -> List[str]:
    echo = False
    with multiprocessing.Pool(processes=n_proc) as pool:
        spans = parts.parts(matcher_tests, n_proc)
        per_proc = pool.map(filter_tests_worker,
                            [(list(span), idx, echo, log_dir) for span, idx in zip(spans, range(n_proc))])
        res = [good_run for p in per_proc for good_run in p]
    return res


def main():
    files_dir = UBUNTU_FILES_DIR
    mined_tests_file = UBUNTU_MINED_MATCHER_TESTS_FILE
    log_dir = UBUNTU_FILTERED_MATCHER_TESTS_LOG_DIR
    filtered_tests_file = UBUNTU_FILTERED_MATCHER_TESTS_FILE
    setup_dir(log_dir)

    shell_parser = BashlexShellParser()
    dockerfile_parser = TPDockerfileParser(shell_parser=shell_parser)
    task_matcher = TaskMatcher()

    n_proc = 6
    # collected_matcher_tests = mine_matcher_tests(df_parser=dockerfile_parser, task_matcher=task_matcher,
    #                                              filepaths=filepaths_from_dir(files_dir),
    #                                              tests_file=mined_tests_file, n_proc=n_proc,)
    collected_matcher_tests = read_matcher_tests(mined_tests_file)[1000:2000]
    filtered_matcher_tests = filter_matcher_tests(collected_matcher_tests, n_proc=n_proc, log_dir=log_dir)

    with open(filtered_tests_file, "w") as outF:
        outF.writelines(t + "\n" for t in filtered_matcher_tests)


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)
    # main()
