import glob
import logging
import exception
import os

import bashlex
import yaml

from log import globalLog

globalLog.setLevel(logging.INFO)


commands_config = {}


def init_commands_config():
    path = './dataset/commands/'
    for filename in glob.glob(os.path.join(path, '*.yml')):
        with open(os.path.join(os.getcwd(), filename), 'r') as _f:  # open in readonly mode
            try:
                commands_config[filename[len(path):filename.find('.yml')]] = yaml.safe_load(_f)
            except yaml.YAMLError as exc:
                globalLog.warning(exc)
                continue


def _scenario_word_is_optional_abstraction_list(s):
    if s[0] == '[' and len(s) >= 5 and s[-4:] == '...]':
        return True
    return False


def _scenario_word_is_optional_abstraction(s):
    if s[0] == '[' and s[-1] == ']' and (len(s) < 5 or s[-4:] != '...]'):
        return True
    return False


def _scenario_word_is_required_abstraction(s):
    if s[0] == '<' and s[-1] == '>':
        return True
    return False


def _scenario_word_is_abstract(s):
    if _scenario_word_is_required_abstraction(s) or \
            _scenario_word_is_optional_abstraction_list(s) or \
            _scenario_word_is_optional_abstraction(s):
        return True
    return False


def _scenario_abstract_word_name(s):
    if _scenario_word_is_required_abstraction(s):
        return s[1:-1]
    if _scenario_word_is_optional_abstraction(s):
        return s[1:-1]
    if _scenario_word_is_optional_abstraction_list(s):
        return s[1:-4]


def _scenario_long_opt_name(s):
    if s.find('=') != -1:
        return s[s.find('--'):s.find('=')]
    return s[s.find('--'):]


def _scenario_short_opt_name(s):
    if s.find('=') != -1:
        return s[s.find('-'):s.find('=')]
    if s.find(',') != -1:
        return s[s.find('-'):s.find(',')]
    return s[s.find('-'):]


def _scenario_fit_opt_type_values(full_value, comm_list):
    return True


def _scenario_fit_opt_type_strings(full_value, comm_list):
    eq_pos = full_value.find('=')
    if eq_pos != -1:
        if eq_pos + 1 >= len(full_value):
            opt_value = ''
        else:
            opt_value = full_value[eq_pos + 1:]
    else:
        if len(comm_list) == 0 or comm_list[0][0] == '-':
            opt_value = ''
        else:
            opt_value = comm_list.pop(0)
    return opt_value


def _scenario_fit_opt_type_paths(full_value, comm_list):
    opt_value = _scenario_fit_opt_type_strings(full_value, comm_list)
    if opt_value == '':
        raise exception.EnrichCommandException('Path option value is not provided')
    return opt_value


def _scenario_fit_opt_type_counts(full_value, comm_list):
    opt_value = 0

    return opt_value


def _scenario_explode_option_list(comm_list):
    if comm_list[0][0:2] == '--':
        values = [comm_list[0]]
    else:
        if comm_list[0].find('=') != -1:
            values = [comm_list[0]]
        else:
            values = ['-' + ch for ch in _scenario_short_opt_name(comm_list[0])[1:]]
            comm_list.pop(0)
            for value in values:
                comm_list.insert(0, value)
    return values


def _scenario_fit_option(scenario, comm_list, node):
    values = _scenario_explode_option_list(comm_list)

    for full_value in values:
        if full_value[0:2] == '--':
            value = _scenario_long_opt_name(full_value)
        else:
            value = _scenario_short_opt_name(full_value)

        fitted_opt = None
        fitted_opt_type = None
        for opt_type in scenario['options']:
            for opt in scenario['options'][opt_type]:
                if value[0:2] == '--':
                    tmp_opt = _scenario_long_opt_name(opt)
                else:
                    tmp_opt = _scenario_short_opt_name(opt)
                if tmp_opt == value:
                    fitted_opt = tmp_opt
                    fitted_opt_type = opt_type
                    break

        if fitted_opt is None:
            raise exception.EnrichCommandException('Unknown option ' + value)

        comm_list.pop(0)
        if fitted_opt_type == 'booleans':
            opt_value = _scenario_fit_opt_type_values(full_value, comm_list)
        elif fitted_opt_type == 'strings':
            opt_value = _scenario_fit_opt_type_strings(full_value, comm_list)
        elif fitted_opt_type == 'paths':
            opt_value = _scenario_fit_opt_type_paths(full_value, comm_list)
        elif fitted_opt_type == 'counts':
            opt_value = _scenario_fit_opt_type_counts(full_value, comm_list)
        else:
            raise exception.EnrichCommandException('Opt type not implemented ' + fitted_opt_type)

        node['options'][fitted_opt] = opt_value


def _scenario_is_suitable(scenario, comm):
    try:
        node = {'type': scenario['name'], 'options': dict()}
        cmd = scenario['cmd'].split()
        comm_list = [child['value'] for child in comm['children']]
        comm_list.pop(0)
        accepting_command_options = True
        for i in range(1, len(cmd)):
            if not _scenario_word_is_abstract(cmd[i]):
                if comm_list[0] != cmd[i]:
                    return False
                comm_list.pop(0)
            else:
                while len(comm_list) and accepting_command_options and comm_list[0][0] == '-':
                    if comm_list[0] == '--':
                        comm_list.pop(0)
                        accepting_command_options = False
                        break
                    _scenario_fit_option(scenario, comm_list, node)
                if _scenario_word_is_required_abstraction(cmd[i]):
                    if len(comm_list) == 0:
                        raise exception.EnrichCommandException('Required argument is not provided')
                    node[_scenario_abstract_word_name(cmd[i])] = comm_list.pop(0)
                elif _scenario_word_is_optional_abstraction(cmd[i]):
                    if len(comm_list):
                        node[_scenario_abstract_word_name(cmd[i])] = comm_list.pop(0)
                elif _scenario_word_is_optional_abstraction_list(cmd[i]):
                    while len(comm_list) > 0:
                        if accepting_command_options and comm_list[0][0] == '-':
                            _scenario_fit_option(scenario, comm_list, node)
                        else:
                            node[_scenario_abstract_word_name(cmd[i])] = comm_list.pop(0)

        if len(comm_list):
            raise exception.EnrichCommandException('Excessive arguments provided')
        return node

    except KeyError as exc:
        globalLog.warning(exc)
        return None
    except exception.EnrichCommandException as exc:
        globalLog.warning(exc)
        globalLog.warning(comm['line'])
        return None


def enrich_command(comm):
    if comm['children'][0]['type'] != 'BASH-WORD' or commands_config.get(comm['children'][0]['value'], None) is None:
        return comm
    else:
        conf = commands_config[comm['children'][0]['value']]['command']
        suitable_scenarios = conf['scenarios'].copy()
        for scenario in suitable_scenarios:
            scenario_res = _scenario_is_suitable(scenario, comm)
            if scenario_res is not None:
                return scenario_res
        return comm


def _bashlex_logical_expression_tree(command_list):
    """
    Assuming that expression is correct
    (this might be already checked by bashlex,
    but might be not)
    """

    # Merging BASH-OPERATOR-AND in one command
    res = []
    i = 0
    prev_command = None
    while i < len(command_list):
        child = command_list[i]
        if child['type'] == 'BASH-COMMAND':
            if prev_command is None:
                prev_command = child
            else:
                res.append(prev_command)
                prev_command = child
        elif child['type'] == 'BASH-OPERATOR-AND':
            prev_command = {'type': 'BASH-OPERATOR-AND', 'children': [prev_command, command_list[i + 1]]}
            i += 1
        elif child['type'] == 'BASH-OPERATOR-OR':
            if prev_command is not None:
                res.append(prev_command)
                prev_command = None
            res.append(child)
        i += 1
    if prev_command is not None:
        res.append(prev_command)

    # Merging BASH-OPERATOR-OR in one command
    command_list = res
    res = []
    i = 0
    prev_command = None
    while i < len(command_list):
        child = command_list[i]
        if child['type'] == 'BASH-COMMAND' or child['type'] == 'BASH-OPERATOR-AND':
            if prev_command is None:
                prev_command = child
            else:
                res.append(prev_command)
                prev_command = child
        elif child['type'] == 'BASH-OPERATOR-OR':
            prev_command = {'type': 'BASH-OPERATOR-OR', 'children': [prev_command, command_list[i + 1]]}
            i += 1
        i += 1
    if prev_command is not None:
        res.append(prev_command)

    return res


def parse_bashlex_list(node, line):
    res = {'type': 'BASH-COMMAND-LIST', 'children': []}
    for part in node.parts:
        child = parse_bashlex(part, line)
        if child is not None:
            res['children'].append(child)

    res['children'] = _bashlex_logical_expression_tree(res['children'])

    return res


def parse_bashlex_command(node, line):
    res = {'type': 'BASH-COMMAND', 'children': [], 'line': line[node.pos[0]:node.pos[1]]}
    for part in node.parts:
        child = parse_bashlex(part, line)
        if child is not None:
            res['children'].append(child)

    return enrich_command(res)


def parse_bashlex_operator(node, line):
    if node.op == ';':
        return None
    elif node.op == '&&':
        return {'type': 'BASH-OPERATOR-AND'}
    elif node.op == '||':
        return {'type': 'BASH-OPERATOR-OR'}


def parse_bashlex_word(node, line):
    if len(node.parts):
        res = {'type': 'BASH-WORD-SUBSTITUTION', 'children': [], 'line': line[node.pos[0]:node.pos[1]]}
        for part in node.parts:
            child = parse_bashlex(part, line)
            if child['type'] == 'BASH-PARAMETER':
                child['pos'] = (child['pos'][0] - node.pos[0], child['pos'][1] - node.pos[0])
                res['children'].append(child)
    else:
        res = {'type': 'BASH-WORD', 'value': line[node.pos[0]:node.pos[1]]}
    return res


def parse_bashlex_parameter(node, line):
    return {'type': 'BASH-PARAMETER', 'value': node.value, 'pos': node.pos}


def parse_bashlex(node, line):
    if node.kind == 'list':
        return parse_bashlex_list(node, line)
    elif node.kind == 'command':
        return parse_bashlex_command(node, line)
    elif node.kind == 'operator':
        return parse_bashlex_operator(node, line)
    elif node.kind == 'word':
        return parse_bashlex_word(node, line)
    elif node.kind == 'parameter':
        return parse_bashlex_parameter(node, line)
    return None


init_commands_config()

with open('./dataset/in.txt', 'r') as inF:
    for bash_line in inF.readlines():
        parts = bashlex.parse(bash_line)
        for ast in parts:
            parsed = parse_bashlex(ast, bash_line)
            print(parsed)

    '''children = [{'type': 'BASH-COMMAND'}, {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-OR'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'}]
    tree = _bashlex_logical_expression_tree(children)
    print(tree)'''
