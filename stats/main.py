import sys
import exception
import stat_bashlex_node
import bashlex

from log import globalLog


EXAMPLE_KIND_BLACKLIST = []
BASHLEX_NODE_KINDS = ['word', 'redirect', 'assignment', 'compound', 'command', 'list',
                      'reservedword', 'operator', 'for', 'function', 'if', 'pipeline', 'pipe']

stats = {kind: list() for kind in BASHLEX_NODE_KINDS}
stats['UNKNOWN'] = []
examples = {}

STAT_NODE = {kind: getattr(stat_bashlex_node, 'stat_' + kind) for kind in BASHLEX_NODE_KINDS}
STAT_NODE['UNKNOWN'] = getattr(stat_bashlex_node, 'stat_unknown')


def _stat_bashlex_node(node):
    kind = node.kind
    if kind not in BASHLEX_NODE_KINDS:
        STAT_NODE['UNKNOWN'](node, stats)
    else:
        STAT_NODE[kind](node, stats)


def _example_bashlex_node(node, top_command_node):
    kind = node.kind
    if kind not in EXAMPLE_KIND_BLACKLIST:
        if examples.get(kind, None) is None:
            examples[kind] = []
        examples[kind].append({'line': line[top_command_node.pos[0]:top_command_node.pos[1]], 'node': top_command_node})


def parse_bashlex_node(line, node, top_command_node=None):
    globalLog.info(node.__dict__)

    if top_command_node is None:
        top_command_node = node
    kind = node.kind
    if kind == 'command':
        top_command_node = node

    _stat_bashlex_node(node)
    _example_bashlex_node(node, top_command_node)

    if hasattr(node, 'parts'):
        for subpart in node.parts:
            parse_bashlex_node(line, subpart, top_command_node)


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as inF:
        for line in inF.readlines():
            parts = bashlex.parse(line)
            for ast in parts:
                print(ast.dump())
                parse_bashlex_node(line, ast, ast)

    print(stats)
