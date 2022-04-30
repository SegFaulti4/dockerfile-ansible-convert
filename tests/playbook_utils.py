import os.path
import os
import zipfile
import shutil
import dockerfile

import docker2ansible.phase_1.process_directive
import docker2ansible.docker2ansible
from docker2ansible.log import globalLog


from utils import DATA_PATH, DOCKERFILES_ARCHIVE_PATH, DOCKERFILES_DIR_PATH, PLAYBOOKS_DIR_PATH, \
    UBUNTU_DOCKERFILES_DIR_PATH, UBUNTU_PLAYBOOKS_DIR_PATH, filenames_from_dir


def _extract_dockerfiles():
    if not os.path.exists(DOCKERFILES_DIR_PATH) or not os.listdir(DOCKERFILES_DIR_PATH):
        globalLog.info('Extracting dockerfiles archive')
        with zipfile.ZipFile(DOCKERFILES_ARCHIVE_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_PATH)
        globalLog.info('Dockerfiles archive extracted')


def _copy_ubuntu_dockerfiles():
    if not os.path.exists(UBUNTU_DOCKERFILES_DIR_PATH) or not os.listdir(UBUNTU_DOCKERFILES_DIR_PATH):
        os.makedirs(UBUNTU_DOCKERFILES_DIR_PATH)

        dockerfiles = filenames_from_dir(DOCKERFILES_DIR_PATH)
        for d in dockerfiles:
            src_path = os.path.join(DOCKERFILES_DIR_PATH, d)
            obj = dockerfile.parse_file(src_path.strip())
            image_name = docker2ansible.phase_1.process_directive.process_from(obj[0])[0]['image_name']
            if image_name == 'ubuntu':
                dst_path = os.path.join(UBUNTU_DOCKERFILES_DIR_PATH, d)
                globalLog.info('Copying Ubuntu dockerfile ' + dst_path)
                shutil.copyfile(src_path, dst_path)


def _setup_playbooks_set(dockerfiles_dir, playbooks_dir):
    dockerfiles = filenames_from_dir(dockerfiles_dir)
    for d in dockerfiles:
        src_path = os.path.join(dockerfiles_dir, d)
        dst_path = os.path.join(playbooks_dir, d[0:d.find('.Dockerfile')] + '.yml')
        dst_stream = open(dst_path, 'a')
        globalLog.info('Converting dockerfile ' + src_path)
        globalLog.info('to ' + dst_path)
        docker2ansible.docker2ansible.main(dockerfile_path=src_path, out_stream=dst_stream)


def setup_main_playbooks_set():
    _extract_dockerfiles()
    if not os.path.exists(PLAYBOOKS_DIR_PATH):
        os.makedirs(PLAYBOOKS_DIR_PATH)
    if not os.listdir(PLAYBOOKS_DIR_PATH):
        _setup_playbooks_set(DOCKERFILES_DIR_PATH, PLAYBOOKS_DIR_PATH)


def setup_ubuntu_playbooks_set():
    _extract_dockerfiles()
    _copy_ubuntu_dockerfiles()
    if not os.path.exists(PLAYBOOKS_DIR_PATH):
        os.makedirs(PLAYBOOKS_DIR_PATH)
    if not os.path.exists(UBUNTU_PLAYBOOKS_DIR_PATH):
        os.makedirs(UBUNTU_PLAYBOOKS_DIR_PATH)
    if not os.listdir(UBUNTU_PLAYBOOKS_DIR_PATH):
        _setup_playbooks_set(UBUNTU_DOCKERFILES_DIR_PATH, UBUNTU_PLAYBOOKS_DIR_PATH)


def setup_playbooks():
    setup_ubuntu_playbooks_set()
    if not os.listdir(PLAYBOOKS_DIR_PATH):
        _setup_playbooks_set(DOCKERFILES_DIR_PATH, PLAYBOOKS_DIR_PATH)


if __name__ == '__main__':
    setup_playbooks()
