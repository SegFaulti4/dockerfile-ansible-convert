import os.path
import os


DATA_PATH = '../data'
DOCKERFILES_ARCHIVE_PATH = os.path.join(DATA_PATH, 'dockerfiles.zip')
DOCKERFILES_DIR_PATH = os.path.join(DATA_PATH, 'dockerfiles')
PLAYBOOKS_DIR_PATH = os.path.join(DATA_PATH, 'playbooks')
UBUNTU_DOCKERFILES_DIR_PATH = os.path.join(DOCKERFILES_DIR_PATH, 'ubuntu')
UBUNTU_PLAYBOOKS_DIR_PATH = os.path.join(PLAYBOOKS_DIR_PATH, 'ubuntu')


def filenames_from_dir(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def filepaths_from_dir(directory):
    return [os.path.join(directory, f) for f in filenames_from_dir(directory)]
