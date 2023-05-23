import os.path
import os
import shutil
from tqdm import tqdm
from typing import List


def _data_structure(data_dir: str):
    _log_dir = os.path.join(data_dir, "log")
    _files_dir = os.path.join(data_dir, "files")
    _stats_dir = os.path.join(data_dir, "stats")

    files_filtered_dir = os.path.join(data_dir, "files_filtered")
    matcher_tests_mined_file = os.path.join(data_dir, "matcher_tests_mined.txt")
    matcher_tests_filtered_file = os.path.join(data_dir, "matcher_tests_filtered.txt")
    commands_mined_file = os.path.join(data_dir, "commands_mined.txt")

    log_files_filtered_dir = os.path.join(_log_dir, 'files_filtered')
    log_matcher_tests_filtered_dir = os.path.join(_log_dir, "matcher_tests_filtered")

    return _log_dir, _files_dir, _stats_dir, \
        files_filtered_dir, matcher_tests_mined_file, \
        matcher_tests_filtered_file, commands_mined_file, \
        log_files_filtered_dir, log_matcher_tests_filtered_dir


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
    UBUNTU_FILES_FILTERED_DIR, UBUNTU_MATCHER_TESTS_MINED_FILE, \
    UBUNTU_MATCHER_TESTS_FILTERED_FILE, UBUNTU_SHELL_COMMANDS_MINED_FILE, \
    UBUNTU_LOG_FILES_FILTERED_DIR, UBUNTU_LOG_MATCHER_TESTS_FILTERED_DIR = _data_structure(UBUNTU_DATA_DIR)

########################
# "ALL" DATA STRUCTURE #
########################

ALL_LOG_DIR, ALL_FILES_DIR, ALL_STATS_DIR, \
    ALL_FILES_FILTERED_DIR, ALL_MINED_MATCHER_TESTS_FILE, \
    ALL_MATCHER_TESTS_FILTERED_FILE, ALL_MINED_SHELL_COMMANDS_FILE, \
    ALL_LOG_FILES_FILTERED_DIR, ALL_LOG_MATCHER_TESTS_FILTERED_DIR = _data_structure(ALL_DATA_DIR)

#########################
# DEBIAN DATA STRUCTURE #
#########################

DEBIAN_LOG_DIR, DEBIAN_FILES_DIR, DEBIAN_STATS_DIR, \
    DEBIAN_FILES_FILTERED_DIR, DEBIAN_MINED_MATCHER_TESTS_FILE, \
    DEBIAN_MATCHER_TESTS_FILTERED_FILE, DEBIAN_MINED_SHELL_COMMANDS_FILE, \
    DEBIAN_LOG_FILES_FILTERED_DIR, DEBIAN_LOG_MATCHER_TESTS_FILTERED_DIR = _data_structure(DEBIAN_DATA_DIR)


def filenames_from_dir(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def filepaths_from_dir(directory: str) -> List[str]:
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def copy_files(paths: List[str], directory: str) -> None:
    for path in tqdm(paths, desc="Copying files", smoothing=1.0):
        shutil.copy2(path, directory)
