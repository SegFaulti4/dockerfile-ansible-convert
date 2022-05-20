import logging
import json

from cotea.runner import runner
from cotea.arguments_maker import argument_maker

import tests.playbook_utils as prepare_playbooks
import tests.utils as utils
from log import globalLog


def run_ansible_check(path):
    maker = argument_maker()
    maker.add_arg("-i", "./localhost_inventory")
    maker.add_arg("--check")
    r = runner(path, maker)

    while r.has_next_play():
        while r.has_next_task():
            tmp = r.run_next_task()
            """if tmp:
                task_res = tmp[0]
                if task_res.is_failed:
                    globalLog.error(task_res.stdout)
                    r.finish_ansible()
                    return "FAILED"""""

    r.finish_ansible()

    if r.was_error():
        print(r.get_error_msg())
        return "FAILED"
    return "OK"


def main():
    globalLog.setLevel(logging.WARNING)
    stats = {"OK": [], "FAILED": []}

    print('Preparing playbooks')
    prepare_playbooks.setup_playbooks()
    print('Playbooks are prepared')
    playbook_paths = utils.filepaths_from_dir(utils.PLAYBOOKS_DIR_PATH)
    for path in playbook_paths:
        print("Running playbook: " + path)
        result = run_ansible_check(path)
        stats[result].append(path)
        print("\t" + result)
    print(json.dumps(stats, indent=4))


if __name__ == '__main__':
    main()
