import logging
import exception
import bashlex

from log import globalLog
globalLog.setLevel(logging.INFO)


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
    return res


def parse_bashlex_operator(node, line):
    if node.op == ';':
        return None
    elif node.op == '&&':
        return {'type': 'BASH-OPERATOR-AND'}
    elif node.op == '||':
        return {'type': 'BASH-OPERATOR-OR'}


def parse_bashlex(node, line):
    if node.kind == 'list':
        return parse_bashlex_list(node, line)
    elif node.kind == 'command':
        return parse_bashlex_command(node, line)
    elif node.kind == 'operator':
        return parse_bashlex_operator(node, line)
    return None


with open('./dataset/in.txt', 'r') as inF:
    for line in inF.readlines():
        parts = bashlex.parse(line)
        for ast in parts:
            parsed = parse_bashlex(ast, line)
            print(parsed)

    '''children = [{'type': 'BASH-COMMAND'}, {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-OR'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'}]
    tree = _bashlex_logical_expression_tree(children)
    print(tree)'''
