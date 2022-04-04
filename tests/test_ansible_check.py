import yaml

import tests.prepare_playbooks as prepare_playbooks
import tests.utils as utils
from docker2ansible.log import globalLog

import ansible_runner
import json
import os
import os.path


def run_ansible_check(path):
    """
    path = os.path.join(os.environ['VIRTUAL_ENV'], 'bin') + ':' + os.environ.get('PATH', '')
    envvars = {
        'PATH': path,
        #'PYTHONPATH': '/home/sprygada/Workspaces/ansible/lib:',
        #'ANSIBLE_ROLES_PATH': '/home/sprygada/Workspaces/roles:',
        #'ANSIBLE_INVENTORY_PLUGIN_EXTS': '.json'
    }
    hosts = {
        'hosts': {
            'localhost': {
                'vars': {
                    'ansible_python_interpreter': 'python',
                    'ansible_connection': 'local'
                }
            }
        }
    }
    """
    playbook = yaml.safe_load(open(path, 'r'))
    # inventory = yaml.safe_load(open('./inventory.yml', 'r'))
    result = ansible_runner.run(playbook=playbook, cmdline='--check')

    stdout = result.stdout.read()
    events = list(result.events)
    stats = result.stats

    print(json.dumps(stats, indent=4))


def main():
    globalLog.info('Preparing playbooks')
    prepare_playbooks.prepare_main_playbooks_set()
    globalLog.info('Playbooks are prepared')
    playbook_paths = utils.filepaths_from_dir(utils.PLAYBOOKS_DIR_PATH)
    for path in playbook_paths:
        run_ansible_check(path)
        break


if __name__ == '__main__':
    main()
