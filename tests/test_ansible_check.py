from cotea.runner import runner
from cotea.arguments_maker import argument_maker

import tests.playbook_utils as prepare_playbooks
import tests.utils as utils
from docker2ansible.log import globalLog


def _is_ignored(task_res):
    return False


def run_ansible_check(path):
    maker = argument_maker()
    maker.add_arg("-i", "./config/inventory")
    maker.add_arg("--check")
    r = runner(path, maker)

    while r.has_next_play():
        while r.has_next_task():
            tmp = r.run_next_task()
            if tmp:
                task_res = tmp[0]
                if task_res.is_failed and not _is_ignored(task_res):
                    globalLog.debug(task_res.stdout)
                    r.finish_ansible()
                    return "FAILED"

    r.finish_ansible()
    return "OK"


def main():
    globalLog.info('Preparing playbooks')
    prepare_playbooks.setup_main_playbooks_set()
    globalLog.info('Playbooks are prepared')
    playbook_paths = utils.filepaths_from_dir(utils.PLAYBOOKS_DIR_PATH)
    for path in playbook_paths:
        globalLog.info("Running playbook: " + path)
        result = run_ansible_check(path)
        globalLog.info("\t" + result)


if __name__ == '__main__':
    main()
