import yaml
import ansible_runner

import tests.playbook_utils as prepare_playbooks
import tests.utils as utils
from docker2ansible.log import globalLog


def run_ansible_check(path):
    playbook = yaml.safe_load(open(path, 'r'))
    inventory = yaml.safe_load(open('./inventory.yml', 'r'))
    result = ansible_runner.run(playbook=playbook, cmdline='--check', inventory=inventory, quiet=True)
    return result


def main():
    globalLog.info('Preparing playbooks')
    prepare_playbooks.setup_main_playbooks_set()
    globalLog.info('Playbooks are prepared')
    playbook_paths = utils.filepaths_from_dir(utils.PLAYBOOKS_DIR_PATH)
    for path in playbook_paths:
        globalLog.info("Running playbook: " + path)
        result = run_ansible_check(path)
        stdout = result.stdout.read()
        events = list(result.events)
        stats = result.stats
        if result.status == 'failed':
            # TODO: add check for copy task failure - such failure doesn't count
            globalLog.info("\tFAILED")
            globalLog.info(stdout)
        else:
            globalLog.info("\tOK")


if __name__ == '__main__':
    main()
