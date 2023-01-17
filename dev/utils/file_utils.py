import os.path
import os
import zipfile
from tqdm import tqdm
from typing import List


DEV_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(os.path.dirname(DEV_DIR), 'data')
CONTAINERFILES_ARCHIVE = os.path.join(DATA_DIR, 'files.zip')
CONTAINERFILES_DIR = os.path.join(DATA_DIR, 'files')


def filenames_from_dir(directory: str) -> List[str]:
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def filepaths_from_dir(directory: str) -> List[str]:
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]


def setup_dir(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)


def extract_containerfiles() -> None:
    setup_dir(CONTAINERFILES_DIR)
    with zipfile.ZipFile(CONTAINERFILES_ARCHIVE, 'r') as zipF:
        for member in tqdm(zipF.infolist(), desc="Extracting"):
            try:
                zipF.extract(member, CONTAINERFILES_DIR)
            except zipfile.error as e:
                pass
