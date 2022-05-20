import logging
import os.path
import os
import zipfile
import time
import yaml
import json

from dockerfile_ansible_convert import dockerfile_ast
from dockerfile_ansible_convert.generator import generate_from_dockerfile, PlaybookGenerator
from log import globalLog


from utils import DATA_PATH, DOCKERFILES_ARCHIVE_PATH, DOCKERFILES_DIR_PATH, PLAYBOOKS_DIR_PATH, \
    UBUNTU_DOCKERFILES_DIR_PATH, UBUNTU_PLAYBOOKS_DIR_PATH, filenames_from_dir


stats = {"OK": 0, "ERROR": []}


def _create_playbook(src_path, dst_path):
    try:
        print('Converting dockerfile ' + src_path + ' to ' + dst_path)
        dst_stream = open(dst_path, 'w')
        ast = dockerfile_ast.create_from_path(src_path)
        playbook = PlaybookGenerator(ast=ast).generate()
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


def _setup_playbooks_set(dockerfiles_dir, playbooks_dir):
    dockerfiles = filenames_from_dir(dockerfiles_dir)
    for d in dockerfiles:
        src_path = os.path.join(dockerfiles_dir, d)
        dst_path = os.path.join(playbooks_dir, d[0:d.find('.Dockerfile')] + '.yml')
        _create_playbook(src_path, dst_path)


def setup_playbooks():
    _extract_dockerfiles()
    if not os.path.exists(PLAYBOOKS_DIR_PATH):
        os.makedirs(PLAYBOOKS_DIR_PATH)
    if not os.listdir(PLAYBOOKS_DIR_PATH):
        _setup_playbooks_set(DOCKERFILES_DIR_PATH, PLAYBOOKS_DIR_PATH)


if __name__ == '__main__':
    globalLog.setLevel(logging.WARNING)
    setup_playbooks()
    print(json.dumps(stats, indent=4))
