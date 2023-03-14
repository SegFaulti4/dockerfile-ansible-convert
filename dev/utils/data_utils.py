import logging
import os.path
import os
import shutil
from tqdm import tqdm
from typing import List, Iterable

from src.shell.main import ShellCommandObject, ShellScript
from src.shell.bashlex.main import BashlexShellParser
from src.containerfile.main import RunDirective, DockerfileContent
from src.containerfile.tpdockerfile.main import TPDockerfileParser
from src.log import globalLog


def _data_structure(data_dir: str):
    log_dir = os.path.join(data_dir, "log")
    files_dir = os.path.join(data_dir, "files")
    stats_dir = os.path.join(data_dir, "stats")

    filtered_files_dir = os.path.join(data_dir, "filtered_files")
    mined_matcher_tests_file = os.path.join(data_dir, "mined_matcher_tests.txt")
    filtered_matcher_tests_file = os.path.join(data_dir, "filtered_matcher_tests.txt")
    mined_shell_commands_file = os.path.join(data_dir, "mined_commands.txt")

    filtered_files_log_dir = os.path.join(log_dir, 'filtered_files')
    filtered_matcher_tests_log_dir = os.path.join(log_dir, "filtered_matcher_tests")

    return log_dir, files_dir, stats_dir, \
        filtered_files_dir, mined_matcher_tests_file, \
        filtered_matcher_tests_file, mined_shell_commands_file, \
        filtered_files_log_dir, filtered_matcher_tests_log_dir


DEV_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(DEV_DIR, 'data')
SANDBOX_DIR = os.path.join(DEV_DIR, 'sandbox')

ALL_DATA_DIR = os.path.join(DATA_DIR, "all")
UBUNTU_DATA_DIR = os.path.join(DATA_DIR, "ubuntu")
DEBIAN_DATA_DIR = os.path.join(DATA_DIR, "debian")

#########################
# UBUNTU DATA STRUCTURE #
#########################

UBUNTU_LOG_DIR, UBUNTU_FILES_DIR, UBUNTU_STATS_DIR, \
    UBUNTU_FILTERED_FILES_DIR, UBUNTU_MINED_MATCHER_TESTS_FILE, \
    UBUNTU_FILTERED_MATCHER_TESTS_FILE, UBUNTU_MINED_SHELL_COMMANDS_FILE, \
    UBUNTU_FILTERED_FILES_LOG_DIR, UBUNTU_FILTERED_MATCHER_TESTS_LOG_DIR = _data_structure(UBUNTU_DATA_DIR)

########################
# "ALL" DATA STRUCTURE #
########################

ALL_LOG_DIR, ALL_FILES_DIR, ALL_STATS_DIR, \
    ALL_FILTERED_FILES_DIR, ALL_MINED_MATCHER_TESTS_FILE, \
    ALL_FILTERED_MATCHER_TESTS_FILE, ALL_MINED_SHELL_COMMANDS_FILE, \
    ALL_FILTERED_FILES_LOG_DIR, ALL_FILTERED_MATCHER_TESTS_LOG_DIR = _data_structure(ALL_DATA_DIR)

#########################
# DEBIAN DATA STRUCTURE #
#########################

DEBIAN_LOG_DIR, DEBIAN_FILES_DIR, DEBIAN_STATS_DIR, \
    DEBIAN_FILTERED_FILES_DIR, DEBIAN_MINED_MATCHER_TESTS_FILE, \
    DEBIAN_FILTERED_MATCHER_TESTS_FILE, DEBIAN_MINED_SHELL_COMMANDS_FILE, \
    DEBIAN_FILTERED_FILES_LOG_DIR, DEBIAN_FILTERED_MATCHER_TESTS_LOG_DIR = _data_structure(DEBIAN_DATA_DIR)


def filenames_from_dir(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def filepaths_from_dir(directory: str) -> List[str]:
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def mine_shell_commands(files_dir: str, output_file: str) -> None:
    sh_parser = BashlexShellParser()
    cf_parser = TPDockerfileParser(shell_parser=sh_parser)

    commands = []
    filenames = filenames_from_dir(files_dir)
    for name in tqdm(filenames, desc="Mining shell"):
        path = os.path.join(files_dir, name)
        try:
            with open(path.strip(), "r") as cf:
                source = "".join(cf.readlines())
                source.replace("\t", " ")

            content = cf_parser.from_str(source)
            for run_dir in content.directives:
                if isinstance(run_dir, RunDirective):
                    line = run_dir.line
                    line.replace("\n", " ")

                    for comm in run_dir.script.parts:
                        if isinstance(comm, ShellCommandObject):
                            line = comm.line
                            line.replace("\t", " ")
                            commands.append(line + "\n")
        except Exception:
            pass

    with open(output_file, "w") as outF:
        outF.writelines(commands)


def copy_files(paths: List[str], directory: str) -> None:
    for path in tqdm(paths, desc="Copying files", smoothing=1.0):
        shutil.copy2(path, directory)


if __name__ == "__main__":
    globalLog.setLevel(logging.ERROR)
