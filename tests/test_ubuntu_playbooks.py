import tests.playbook_utils as playbook_utils
import tests.utils as utils
import tests.instance_utils as instance_utils
from docker2ansible.log import globalLog

from cotea.runner import runner
from cotea.arguments_maker import argument_maker


def run_playbook_on_remote_host(path):
    pb_path = path
    inv_path = "config/inventory"

    arg_maker = argument_maker()
    arg_maker.add_arg("-i", inv_path)

    r = runner(pb_path, arg_maker)

    while r.has_next_play():
        while r.has_next_task():
            r.run_next_task()

    r.finish_ansible()

    if r.was_error():
        print("ansible-playbook launch - ERROR:")
        print(r.get_error_msg())
    else:
        print("ansible-playbook launch - OK")


def main():
    instance_utils.setup_instance()

    globalLog.info('Preparing UBUNTU playbooks')
    playbook_utils.setup_ubuntu_playbooks_set()
    globalLog.info('Playbooks are prepared')
    playbook_paths = utils.filepaths_from_dir(utils.UBUNTU_PLAYBOOKS_DIR_PATH)
    for path in playbook_paths:
        globalLog.info("Running playbook: " + path + " on remote host")
        run_playbook_on_remote_host(path)
        break

    instance_utils.teardown_instance()


if __name__ == '__main__':
    main()
