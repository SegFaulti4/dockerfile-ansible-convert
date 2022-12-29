import os.path
import os
import zipfile
from typing import List


DATA_DIR = "./data"
ARCHIVE_PATH = f"{DATA_DIR}/files.zip"
FILES_DIR = f"{DATA_DIR}/files"


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def filenames_from_dir(directory: str) -> List[str]:
    return sorted([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])


def filepaths_from_dir(directory: str) -> List[str]:
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]


def extract_files() -> None:
    setup_dir(FILES_DIR)
    with zipfile.ZipFile(ARCHIVE_PATH, 'r') as zipF:
        zipF.extractall(FILES_DIR)
