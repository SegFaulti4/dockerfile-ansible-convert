import os.path
import os
import zipfile
from typing import List


SANDBOX_DIR = "../"
DOCKERFILES_DIR = f"{SANDBOX_DIR}/data/dockerfiles"
DOCKERFILES_ARCHIVE = f"{SANDBOX_DIR}/data/dockerfiles.zip"


def filenames_from_dir(directory: str) -> List[str]:
    return sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])


def filepaths_from_dir(directory: str) -> List[str]:
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def extract_dockerfiles() -> None:
    setup_dir(DOCKERFILES_DIR)
    with zipfile.ZipFile(DOCKERFILES_ARCHIVE, 'r') as zipF:
        zipF.extractall(DOCKERFILES_DIR)


if __name__ == "__main__":
    extract_dockerfiles()
