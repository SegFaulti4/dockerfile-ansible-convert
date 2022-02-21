import sys
import argparse
import json
import logging
import yaml

import exception
from log import globalLog
from ast2playbook.match_module import match_ansible_module, default_match


globalLog.setLevel(logging.DEBUG)


class Global:
    BASH_COMMAND_COUNT = 0
    REGISTER_COUNT = 0


def load_phase_3(in_stream):
    return json.load(in_stream)


def _register_name(reg_num):
    return 'auto_generated_register_' + str(reg_num)


def new_register_name():
    Global.REGISTER_COUNT += 1
    return _register_name(Global.REGISTER_COUNT)


def prev_register_name():
    return _register_name(Global.REGISTER_COUNT)


def new_task_name():
    Global.BASH_COMMAND_COUNT += 1
    return 'Generated task ' + str(Global.BASH_COMMAND_COUNT)


def match_ansible_task(new_task, command):
    try:
        match = None
        if command['type'] == 'MAYBE-BASH':
            match = {'shell': {'cmd': command['value']}}
        elif command['type'] == 'BASH-COMMAND':
            match = default_match(command)
        elif command['type'] == 'ENRICHED-COMMAND':
            match = match_ansible_module(command)
        if match is None:
            globalLog.warning('Unknown command type ' + command['type'])
        else:
            for key in match:
                new_task[key] = match[key]
    except exception.MatchAnsibleModuleException as exc:
        globalLog.info(exc)
        globalLog.info('Failed to match command ' + command['name'])
        globalLog.info('Resolving to shell: ' + command['line'])
        new_task['shell'] = command['line']


def bash_command_to_task(ansible_ast, command, pass_register=False):
    if command['type'] == 'BASH-COMMAND-LIST':
        for child in command['children']:
            bash_command_to_task(ansible_ast, child)
    elif command['type'] == 'BASH-OPERATOR-AND' or command['type'] == 'BASH-OPERATOR-OR':
        bash_command_to_task(ansible_ast, command['children'][0], pass_register=True)
        bash_command_to_task(ansible_ast, command['children'][1], pass_register=pass_register)
        if command['type'] == 'BASH-OPERATOR-AND':
            ansible_ast['tasks'][-1]['when'] = prev_register_name() + ' is succeeded'
        elif command['type'] == 'BASH-OPERATOR-OR':
            ansible_ast['tasks'][-1]['when'] = prev_register_name() + ' is not succeeded'
    else:
        new_task = {'name': new_task_name()}
        if pass_register:
            new_task['register'] = new_register_name()

        match_ansible_task(new_task, command)
        ansible_ast['tasks'].append(new_task)


def handle_docker_ast_default(directive):
    globalLog.info('Docker AST node type ' + directive['type'] + ' is not implemented')


def handle_docker_ast_run(ansible_ast, directive):
    for child in directive['children']:
        bash_command_to_task(ansible_ast, child)


def docker2ansible(docker_ast):
    Global.BASH_COMMAND_COUNT = 0
    Global.REGISTER_COUNT = 0

    res = {'hosts': 'localhost',
           'name': 'Generated from dockerfile',
           'tasks': list()}

    if docker_ast['type'] != 'DOCKER-FILE':
        raise exception.GenerateAnsibleASTException('Wrong node type provided ' + docker_ast['type'])

    for directive in docker_ast['children']:
        if directive['type'] == 'DOCKER-RUN':
            handle_docker_ast_run(res, directive)
        else:
            handle_docker_ast_default(directive)

    return [res]


def dump_playbook(ansible_ast, filename):
    try:
        out_file = open(filename, 'w')
        yaml.dump(ansible_ast, out_file)
    except Exception as exc:
        globalLog.error(exc)


def dump_playbooks(in_stream):
    ph_3 = load_phase_3(in_stream)
    for docker_ast in ph_3:
        ansible_ast = {}
        try:
            ansible_ast = docker2ansible(docker_ast)
        except exception.GenerateAnsibleASTException as exc:
            globalLog.warning(exc)
            globalLog.warning("Couldn't generate playbook from docker AST")
        except Exception as exc:
            globalLog.error(type(exc))
            globalLog.error(exc)
            globalLog.error("Couldn't generate playbook from docker AST")
        meta_info = docker_ast['meta_info']
        dump_playbook(ansible_ast, './dataset/playbooks/' +
                      meta_info[meta_info.rfind('/') + 1:meta_info.find('.Dockerfile')] + '.yml')


def main():
    dump_playbooks(open("./dataset/phase_3.json", 'r'))


if __name__ == '__main__':
    main()
