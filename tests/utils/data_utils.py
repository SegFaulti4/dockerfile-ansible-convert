import shutil
import os.path


TESTS_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(TESTS_DIR, "data")
LOG_DIR = os.path.join(DATA_DIR, "log")
TMP_DIR = os.path.join(DATA_DIR, "tmp")

GENERATOR_TESTS_DIR = os.path.join(DATA_DIR, "generator_tests")


def copy_file(src: str, dst: str) -> None:
    shutil.copy2(src, dst)


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)
