import subprocess
from subprocess import PIPE

import dev.stats.utils as utils
from src.ansible_generator.main import *
from src.ansible_matcher.main import *
from src.containerfile.tpdockerfile.main import *
from src.shell.bashlex.main import *
from dev.utils.data_utils import *


def mine_matcher_tests(df_parser: DockerfileParser, task_matcher: TaskMatcher,
                       filepaths: List[str], tests_file: str) -> List[str]:
    matcher_tests = []

    for path in tqdm(filepaths, desc="Collecting matcher tests", smoothing=1.0):
        matcher_tests.extend(_matcher_tests_miner(path, df_parser=df_parser, task_matcher=task_matcher))

    matcher_tests = list(dict.fromkeys(matcher_tests))
    with open(tests_file, "w") as outF:
        outF.writelines(t + "\n" for t in matcher_tests)
    return matcher_tests


def _matcher_tests_miner(filepath: str, df_parser: DockerfileParser, task_matcher: TaskMatcher) -> List[str]:
    try:
        with open(filepath.strip(), "r") as df:
            source = "".join(df.readlines())

        content = df_parser.from_str(source)
        generator = RoleGenerator(tm=task_matcher, dc=content)
        generator.collect_matcher_tests = True
        generator.generate()
        tests = generator.matcher_tests

    except Exception as exc:
        globalLog.info(type(exc), exc)
        tests = []

    return tests


def read_matcher_tests(tests_file: str) -> List[str]:
    with open(tests_file, "r") as inF:
        tests = [line.strip() for line in inF]
    return tests


def filter_matcher_tests(matcher_tests: List[str], n_proc: int, log_dir: str) -> List[str]:
    return utils.map_reduce(worker=_filter_tests_worker, data=matcher_tests, n_proc=n_proc, log_dir=log_dir)


def _filter_tests_worker(args: Tuple[List[str], int, bool, str]) -> List[str]:
    tests, idx, echo, log_dir = args
    filtered = []

    log_path = os.path.join(log_dir, f"filter-tests-{idx}")
    with open(log_path, "w") as logF:
        with tqdm(total=len(tests), position=idx, desc=f"Loop {idx}") as pbar:
            for i, test in enumerate(tests):
                container_name = f"ubuntu-test-{idx}-{i}"
                run_comm = f'docker run --name={container_name} ubuntu-test-stand bash -c "{test}"'
                inspect_comm = f'docker inspect {container_name} --format="{{{{.State.ExitCode}}}}"'
                stop_rm_comm = f'docker stop {container_name} && docker rm {container_name}'

                try:
                    utils.flag_print(run_comm, echo=echo)
                    run_result = subprocess.run(['/bin/bash', '-c', run_comm],
                                                stdout=PIPE, stderr=PIPE, text=True, timeout=120)
                    utils.flag_print(inspect_comm, echo=echo)
                    inspect_result = subprocess.run(['/bin/bash', '-c', inspect_comm], stdout=PIPE, stderr=PIPE, text=True)

                    success = True if not inspect_result.stderr and inspect_result.stdout.strip() == "0" else False
                    run_stdout, run_stderr = run_result.stdout, run_result.stderr
                except subprocess.TimeoutExpired:
                    success = False
                    run_stdout, run_stderr = "", "Time limit exceeded"
                if success:
                    filtered.append(test)

                utils.flag_print(stop_rm_comm, echo=echo)
                subprocess.run(['/bin/bash', '-c', stop_rm_comm], stdout=PIPE, stderr=PIPE, text=True)

                logF.writelines([
                    utils.log_header("run command") + f"{run_comm}\n\n",
                    utils.log_header("run stdout") + f"{run_stdout}\n\n",
                    utils.log_header("run stderr") + f"{run_stderr}\n\n",
                    utils.log_header("success") + f"{success}\n\n"
                ])
                pbar.update(1)

    return filtered


def main():
    files_dir = UBUNTU_FILES_FILTERED_DIR
    filepaths = filepaths_from_dir(files_dir)
    tests_file = UBUNTU_MATCHER_TESTS_MINED_FILE
    log_dir = UBUNTU_LOG_MATCHER_TESTS_FILTERED_DIR
    filtered_tests_file = UBUNTU_MATCHER_TESTS_FILTERED_FILE
    setup_dir(log_dir)

    n_proc = 2
    dfp, tm = TPDockerfileParser(shell_parser=BashlexShellParser()), TaskMatcher()

    matcher_tests = mine_matcher_tests(df_parser=dfp, task_matcher=tm, filepaths=filepaths, tests_file=tests_file)
    # matcher_tests = read_matcher_tests(tests_file)
    filtered_matcher_tests = filter_matcher_tests(matcher_tests, n_proc=n_proc, log_dir=log_dir)

    with open(filtered_tests_file, "w") as outF:
        outF.writelines(t + "\n" for t in filtered_matcher_tests)


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)
    # main()
