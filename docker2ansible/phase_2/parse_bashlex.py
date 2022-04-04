import bashlex

from docker2ansible.log import globalLog


BASH_WORD_SUBSTITUTION_CHILDREN_TYPES = ['BASH-PARAMETER', 'BASH-VALUE']


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
    # check if it's an assignment
    if node.word[0] != '-':
        eq_pos = node.word.find('=')
        if eq_pos != -1 and all(x.pos[0] > eq_pos + node.pos[0] for x in node.parts):
            return parse_bashlex_assignment(node, line)

        if eq_pos != -1:
            globalLog.info("Unexpected '=' symbol in word node " + node.dump())

    if len(node.parts):
        res = {'type': 'BASH-WORD-PARAMETERIZED', 'children': [], 'value': line[node.pos[0]:node.pos[1]]}
        for part in node.parts:
            child = parse_bashlex_node(part, line)
            if not child:
                return []
            for param in filter(lambda x: x['type'] in BASH_WORD_SUBSTITUTION_CHILDREN_TYPES, child):
                if param['type'] != 'BASH-PARAMETER':
                    res['type'] = 'BASH-WORD-SUBSTITUTION'
                param['pos'] = (param['pos'][0] - node.pos[0], param['pos'][1] - node.pos[0])
                res['children'].append(param)
    else:
        res = {'type': 'BASH-WORD', 'value': line[node.pos[0]:node.pos[1]]}
    return [res]


def parse_bashlex_parameter(node, line):
    return [{'type': 'BASH-PARAMETER', 'name': node.value, 'pos': node.pos}]


def parse_bashlex_bash_value(value):
    nodes = bashlex.parse(value)
    # if it's a simple list of words - leave it as it is
    # if not - let the shell do the work
    if len(nodes) == 1 and nodes[0].kind == 'command' and \
            all(part.kind == 'word' and not part.parts for part in nodes[0].parts):
        return {'type': 'STRING-CONSTANT', 'value': value}
    else:
        return {'type': 'BASH-VALUE', 'value': value}


def parse_bashlex_assignment(node, line):
    eq_pos = node.word.find('=')
    name, value = node.word[0:eq_pos], node.word[eq_pos + 1:]
    return [{
        'type': 'BASH-ASSIGNMENT',
        'name': name,
        'children': [parse_bashlex_bash_value(value)]
    }]


def parse_bashlex_commandsubstitution(node, line):
    return [{
        'type': 'BASH-VALUE',
        'value': line[node.pos[0]:node.pos[1]],
        'pos': (node.pos[0], node.pos[1])
    }]


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
    elif node.kind == 'assignment':
        return parse_bashlex_assignment(node, line)
    elif node.kind == 'commandsubstitution':
        return parse_bashlex_commandsubstitution(node, line)
    globalLog.info('Bashlex node kind "' + node.kind + '" is not supported')
    return []
