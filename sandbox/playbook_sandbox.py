import logging

from docker2ansible.log import globalLog

from cotea.runner import runner
from cotea.arguments_maker import argument_maker


def main():
    maker = argument_maker()
    maker.add_arg("-i", "../../tests/config/inventory")
    r = runner("./data/dockerfile_sandbox.yml", maker)

    while r.has_next_play():
        while r.has_next_task():
            r.run_next_task()

    r.finish_ansible()

    if r.was_error():
        print("ansible-playbook launch - ERROR:")
        print(r.get_error_msg())
    else:
        print("ansible-playbook launch - OK")


if __name__ == '__main__':
    globalLog.setLevel(logging.INFO)
    main()
