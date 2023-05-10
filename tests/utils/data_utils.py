import shutil
import os.path
from typing import List


TESTS_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(TESTS_DIR, "data")
LOG_DIR = os.path.join(DATA_DIR, "log")
TMP_DIR = os.path.join(DATA_DIR, "tmp")

GENERATOR_TESTS_DIR = os.path.join(DATA_DIR, "generator_tests")
PATCHED_GENERATOR_TESTS_DIR = os.path.join(DATA_DIR, "patched_generator_tests")
GENERATOR_TEST_IMAGES_FILE = os.path.join(DATA_DIR, "generator_test_images.txt")


def copy_file(src: str, dst: str) -> None:
    shutil.copy2(src, dst)


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def filenames_from_dir(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
