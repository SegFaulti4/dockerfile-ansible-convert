import json
import logging
import yaml

import exception
from log import globalLog
from ast2playbook.match_module.main import match_ansible_module, default_match


globalLog.setLevel(logging.DEBUG)


class Global:
    BASH_COMMAND_COUNT = 0
    REGISTER_COUNT = 0
    stack = dict()
    directive_stack = dict()
    cur_playbook = dict()


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


def _last_task():
    return Global.cur_playbook['tasks'][-1]


def wrap_ansible_matched_module_task(task):
    # TODO
    pass


def wrap_ansible_shell_task(task):
    # TODO
    pass


def handle_bash_default(obj):
    handle_default(obj)


def handle_bash_variable_definition(obj):
    # TODO
    pass


def _handle_bash_operator_general(obj):
    ast2playbook_ast_visit(obj['children'][0])
    _last_task()['register'] = new_register_name()
    ast2playbook_ast_visit(obj['children'][1])


def handle_bash_operator_or(obj):
    _handle_bash_operator_general(obj)
    _last_task()['when'] = prev_register_name() + ' is not succeeded'


def handle_bash_operator_and(obj):
    _handle_bash_operator_general(obj)
    _last_task()['when'] = prev_register_name() + ' is succeeded'


def handle_bash_command_enriched(obj):
    match = match_ansible_module(obj)

    if match:
        Global.cur_playbook['tasks'].append(match)
        wrap_ansible_matched_module_task(_last_task())
    else:
        globalLog.info('Failed to match command ' + obj['name'])
        globalLog.info('Resolving to shell: ' + obj['line'])
        _handle_bash_with_default_match(obj)


def _handle_bash_with_default_match(obj):
    match = default_match(obj)
    Global.cur_playbook['tasks'].append(match)
    wrap_ansible_shell_task(_last_task())


def handle_bash_command(obj):
    _handle_bash_with_default_match(obj)


def handle_maybe_bash(obj):
    _handle_bash_with_default_match(obj)


def handle_docker_ast_default(obj):
    handle_default(obj)


def handle_docker_ast_run(directive):
    Global.directive_stack = dict()
    for child in directive['children']:
        ast2playbook_ast_visit(child)


def handle_docker_ast_env(obj):
    Global.stack[obj['name']] = obj['children'][0]
    if obj['children'][0]['type'] == 'BASH-VALUE':
        Global.cur_playbook['tasks'].append({
            'shell': {
                'cmd': 'echo "' + obj['children'][0]['value'] + '"'
            },
            'register': new_register_name()
        })
        wrap_ansible_shell_task(_last_task())
        Global.stack[obj['name']]['register'] = _last_task()['register']
    # TODO: add set_fact task


def handle_default(obj):
    globalLog.info('Docker AST node type ' + obj['type'] + ' is not implemented')


def ast2playbook_ast_visit(obj):
    if obj['type'].find('DOCKER') == 0:
        if obj['type'] == 'DOCKER-FROM':
            handle_docker_ast_default(obj)
        elif obj['type'] == 'DOCKER-RUN':
            handle_docker_ast_run(obj)
        elif obj['type'] == 'DOCKER-ENV':
            handle_docker_ast_env(obj)
        else:
            handle_docker_ast_default(obj)
    elif obj['type'].find('BASH') == 0:
        if obj['type'].find('BASH-COMMAND') == 0:
            if obj['type'] == 'BASH-COMMAND':
                handle_bash_command(obj)
            elif obj['type'] == 'BASH-COMMAND-ENRICHED':
                handle_bash_command_enriched(obj)
        elif obj['type'].find('BASH-OPERATOR') == 0:
            if obj['type'] == 'BASH-OPERATOR-AND':
                handle_bash_operator_and(obj)
            elif obj['type'] == 'BASH-OPERATOR-OR':
                handle_bash_operator_or(obj)
            else:
                handle_bash_default(obj)
        elif obj['type'] == 'BASH-VARIABLE-DEFINITION':
            handle_bash_variable_definition(obj)
        else:
            handle_bash_default(obj)
    elif obj['type'] == 'MAYBE-BASH':
        handle_maybe_bash(obj)
    else:
        handle_default(obj)


def ast2playbook_process(docker_ast):
    Global.BASH_COMMAND_COUNT = 0
    Global.REGISTER_COUNT = 0
    Global.stack = dict()
    Global.cur_playbook = {
        'hosts': 'default',
        'name': 'Generated from dockerfile',
        'tasks': list()
    }

    if docker_ast['type'] != 'DOCKER-FILE':
        raise exception.GenerateAnsibleASTException('Wrong node type provided ' + docker_ast['type'])
    for obj in docker_ast['children']:
        ast2playbook_ast_visit(obj)

    return [Global.cur_playbook]


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
            ansible_ast = ast2playbook_process(docker_ast)
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
