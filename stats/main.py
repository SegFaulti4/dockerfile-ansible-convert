import sys
import exception
import logging
import stat_bashlex_node
import bashlex

from bashlex.errors import ParsingError
from log import globalLog
globalLog.setLevel(logging.DEBUG)


EXAMPLE_KIND_BLACKLIST = []
BASHLEX_NODE_KINDS = ['word', 'redirect', 'assignment', 'compound', 'command', 'list',
                      'reservedword', 'operator', 'for', 'function', 'if', 'pipeline', 'pipe',
                      'parameter', 'commandsubstitution', 'tilde', 'while']

stats = {kind: {'values': list()} for kind in BASHLEX_NODE_KINDS}
stats['operator'] = {}
stats['word'] = {'trivial_count': 0, 'parent_count': {}}
stats['UNKNOWN'] = {'values': list()}
stats['usage'] = []
examples = {}

STAT_NODE = {kind: getattr(stat_bashlex_node, 'stat_' + kind) for kind in BASHLEX_NODE_KINDS}
STAT_NODE['UNKNOWN'] = getattr(stat_bashlex_node, 'stat_unknown')


def _stat_bashlex_node(node):
    if stats['usage'][-1].get(node.kind, None) is None:
        stats['usage'][-1][node.kind] = 0
    stats['usage'][-1][node.kind] += 1
    kind = node.kind
    if kind not in BASHLEX_NODE_KINDS:
        STAT_NODE['UNKNOWN'](node, stats)
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
        with open('./dataset/' + ex_dir + '/' + key, 'w') as outF:
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


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as inF:
        for line in inF.readlines():
            try:
                parts = bashlex.parse(line)
                for ast in parts:
                    globalLog.debug(line)
                    globalLog.debug(ast.dump())

                    # TODO: find more suitable design
                    stats['usage'].append(dict())

                    mine_bashlex_node(line, ast, ast)
            except ParsingError as er:
                continue
            except NotImplementedError as er:
                continue

    usages = {kind: 0 for kind in BASHLEX_NODE_KINDS}
    for usage in stats['usage']:
        for key in usage:
            usages[key] += 1

    pass
    # dump_examples()
