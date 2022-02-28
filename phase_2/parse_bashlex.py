import exception
from log import globalLog


def _bashlex_logical_expression_tree(command_list):
    """
    Assuming that expression is correct
    (this might be already checked by bashlex,
    but might be not)
    """

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
            prev_command = {'type': 'BASH-OPERATOR-OR', 'children': [prev_command, command_list[i + 1]]}
            i += 1
        i += 1
    if prev_command is not None:
        res.append(prev_command)

    return res


def parse_bashlex_list(node, line):
    res = []
    for part in node.parts:
        child = parse_bashlex_node(part, line)
        if not child:
            return []
        res.extend(filter(lambda x: x['type'] != 'BASH-EOC', child))

    res = _bashlex_logical_expression_tree(res)
    return res


def parse_bashlex_command(node, line):
    res = {'type': 'BASH-COMMAND', 'children': [], 'line': line[node.pos[0]:node.pos[1]]}
    for part in node.parts:
        child = parse_bashlex_node(part, line)
        if not child:
            return []
        res['children'].extend(child)

    return [res]


def parse_bashlex_operator(node, line):
    if node.op == ';':
        return [{'type': 'BASH-EOC'}]
    elif node.op == '&&':
        return [{'type': 'BASH-OPERATOR-AND'}]
    elif node.op == '||':
        return [{'type': 'BASH-OPERATOR-OR'}]


def parse_bashlex_word(node, line):
    if len(node.parts):
        res = {'type': 'BASH-WORD-SUBSTITUTION', 'children': [], 'line': line[node.pos[0]:node.pos[1]]}
        for part in node.parts:
            child = parse_bashlex_node(part, line)
            if not child:
                return []
            for param in filter(lambda x: x['type'] == 'BASH-PARAMETER', child):
                param['pos'] = (param['pos'][0] - node.pos[0], param['pos'][1] - node.pos[0])
                res['children'].append(param)
    else:
        res = {'type': 'BASH-WORD', 'value': line[node.pos[0]:node.pos[1]]}
    return [res]


def parse_bashlex_parameter(node, line):
    return [{'type': 'BASH-PARAMETER', 'value': node.value, 'pos': node.pos}]


def parse_bashlex_node(node, line):
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
    globalLog.info('Bashlex node kind "' + node.kind + '" is not supported')
    return []
