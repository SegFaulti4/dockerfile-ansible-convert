import sys
import logging
import bashlex_stat.stat_node
import bashlex

from bashlex.errors import ParsingError
from docker2ansible.log import globalLog
globalLog.setLevel(logging.DEBUG)


EXAMPLE_KIND_BLACKLIST = []
BASHLEX_NODE_KINDS = ['word', 'redirect', 'assignment', 'compound', 'command', 'list',
                      'reservedword', 'operator', 'for', 'function', 'if', 'pipeline', 'pipe',
                      'parameter', 'commandsubstitution', 'tilde', 'while', 'until', 'heredoc',
                      'processsubstitution', 'unknown']
BLANK_BASHLEX_NODE_INDEX = {kind: 0 for kind in BASHLEX_NODE_KINDS}


stats = {'values': {kind: dict() for kind in BASHLEX_NODE_KINDS},
         'usages': BLANK_BASHLEX_NODE_INDEX.copy(),
         'appearances': BLANK_BASHLEX_NODE_INDEX.copy(),
         'last_line_appearances': BLANK_BASHLEX_NODE_INDEX.copy()}
examples = {}

STAT_NODE = {kind: getattr(bashlex_stat.stat_node, 'stat_' + kind) for kind in BASHLEX_NODE_KINDS}


def _stat_bashlex_node(node):
    kind = node.kind
    if kind not in BASHLEX_NODE_KINDS:
        STAT_NODE['unknown'](node, stats)
    else:
        STAT_NODE[kind](node, stats)


def _example_bashlex_node(node, top_command_node, line):
    kind = node.kind
    if kind not in EXAMPLE_KIND_BLACKLIST:
        if examples.get(kind, None) is None:
            examples[kind] = []
        examples[kind].append({
            'line': line[top_command_node.pos[0]:top_command_node.pos[1]],
            'node': top_command_node
        })


def dump_examples(ex_dir=None):
    if ex_dir is None:
        ex_dir = 'bashlex_examples'

    for key in examples:
        with open('./' + ex_dir + '/' + key, 'w') as outF:
            old_stdout = sys.stdout
            sys.stdout = outF
            i = 1
            for example in examples[key]:
                print(str(i) + ') ' + example['line'] + '\n')
                print(example['node'].dump() + '\n\n')
                i += 1
            sys.stdout = old_stdout


def mine_bashlex_node(line, node, top_command_node=None):
    globalLog.info(node.__dict__)

    if top_command_node is None:
        top_command_node = node
    kind = node.kind
    if kind == 'command':
        top_command_node = node

    _stat_bashlex_node(node)
    # _example_bashlex_node(node, top_command_node, line)

    if hasattr(node, 'parts'):
        for subpart in node.parts:
            mine_bashlex_node(line, subpart, top_command_node)

    if hasattr(node, 'list'):
        for subpart in node.list:
            mine_bashlex_node(line, subpart, top_command_node)


def mine_bash_line(line):
    parts = bashlex.parse(line)
    for ast in parts:
        globalLog.debug(line)
        globalLog.debug(ast.dump())
        mine_bashlex_node(line, ast, ast)

    for bucket in stats['last_line_appearances']:
        stats['appearances'][bucket] += stats['last_line_appearances'][bucket]

    stats['last_line_appearances'] = BLANK_BASHLEX_NODE_INDEX.copy()


with open('./mined', 'r') as inF:
    CUR_BASH_LINE_IDX = 0

    for line in inF.readlines():
        try:
            mine_bash_line(line)
        except ParsingError as er:
            continue
        except NotImplementedError as er:
            continue

    pass
    # dump_examples()
