import logging
import os.path
import os
import zipfile
import shutil
import dockerfile
import time
import yaml
import json

import dockerfile_ansible_convert.main as main
from dockerfile_ansible_convert.generator import generate_from_dockerfile
from log import globalLog


from utils import DATA_PATH, DOCKERFILES_ARCHIVE_PATH, DOCKERFILES_DIR_PATH, PLAYBOOKS_DIR_PATH, \
    UBUNTU_DOCKERFILES_DIR_PATH, UBUNTU_PLAYBOOKS_DIR_PATH, filenames_from_dir


stats = {"OK": 0, "ERROR": []}


def _create_playbook(src_path, dst_path):
    try:
        print('Converting dockerfile ' + src_path + ' to ' + dst_path)
        dst_stream = open(dst_path, 'w')
        playbook = generate_from_dockerfile(src_path)
        yaml.dump(playbook, dst_stream)
        time.sleep(0.05)
    except Exception:
        stats["ERROR"].append(src_path)
        print("ERROR")
    else:
        stats["OK"] += 1
        print("OK")


def _extract_dockerfiles():
    if not os.path.exists(DOCKERFILES_DIR_PATH) or not os.listdir(DOCKERFILES_DIR_PATH):
        print('Extracting dockerfiles archive')
        with zipfile.ZipFile(DOCKERFILES_ARCHIVE_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_PATH)
        print('Dockerfiles archive extracted')


def _copy_ubuntu_dockerfiles():
    if not os.path.exists(UBUNTU_DOCKERFILES_DIR_PATH) or not os.listdir(UBUNTU_DOCKERFILES_DIR_PATH):
        os.makedirs(UBUNTU_DOCKERFILES_DIR_PATH)

        dockerfiles = filenames_from_dir(DOCKERFILES_DIR_PATH)
        for d in dockerfiles:
            src_path = os.path.join(DOCKERFILES_DIR_PATH, d)
            obj = dockerfile.parse_file(src_path.strip())
            if obj[0].value[0].find("ubuntu") != -1 or obj[0].value[0].find("centos") != -1:
                dst_path = os.path.join(UBUNTU_DOCKERFILES_DIR_PATH, d)
                print('Copying Ubuntu dockerfile ' + dst_path)
                shutil.copyfile(src_path, dst_path)


def _setup_playbooks_set(dockerfiles_dir, playbooks_dir):
    dockerfiles = filenames_from_dir(dockerfiles_dir)
    for d in dockerfiles:
        src_path = os.path.join(dockerfiles_dir, d)
        dst_path = os.path.join(playbooks_dir, d[0:d.find('.Dockerfile')] + '.yml')
        _create_playbook(src_path, dst_path)


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
    if len(os.listdir(PLAYBOOKS_DIR_PATH)) <= 1:
        _setup_playbooks_set(DOCKERFILES_DIR_PATH, PLAYBOOKS_DIR_PATH)


if __name__ == '__main__':
    globalLog.setLevel(logging.WARNING)
    setup_playbooks()
    print(json.dumps(stats, indent=4))
