import json
import logging

import docker2ansible.phase_1.phase_1
import docker2ansible.phase_2.phase_2
import docker2ansible.phase_3.phase_3
import docker2ansible.phase_3.enrich
import docker2ansible.ast2playbook.ast2playbook

from docker2ansible.log import globalLog


def fancy_print(ast):
    print(json.dumps(ast, indent=4, sort_keys=True))


def main():
    dockerfile_path = 'dockerfile_sandbox'
    playbook_path = './dockerfile_sandbox.yml'
    ast = docker2ansible.phase_1.phase_1.parse_dockerfile_from_path(dockerfile_path)
    ast = docker2ansible.phase_1.phase_1.phase_1_process(parsed_dockerfile=ast, meta_info=dockerfile_path)
    ast = docker2ansible.phase_2.phase_2.phase_2_process(obj=ast)
    ast = docker2ansible.phase_3.phase_3.phase_3_process(obj=ast)
    ast = docker2ansible.ast2playbook.ast2playbook.ast2playbook_process(ast)
    docker2ansible.ast2playbook.ast2playbook.dump_playbook(ast, open(playbook_path, 'w'))
    fancy_print(ast)


if __name__ == '__main__':
    globalLog.setLevel(logging.INFO)
    main()
