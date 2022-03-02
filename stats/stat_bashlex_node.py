import bashlex.ast

import exception
import sys
import logging

from log import globalLog
globalLog.setLevel(logging.INFO)


def _stat_default(bucket, node, stats):
    stats['usages'][bucket] += 1
    if stats['last_line_appearances'][bucket] == 0:
        stats['last_line_appearances'][bucket] = 1

    d = dict(node.__dict__)
    for key, value in sorted(d.items()):
        if stats['values'][bucket].get(key, None) is None:
            stats['values'][bucket][key] = {}
        values = []
        if isinstance(value, list):
            values = value
        else:
            values.append(value)

        for v in values:
            if isinstance(v, bashlex.ast.node):
                if stats['values'][bucket][key].get(v.kind, None) is None:
                    stats['values'][bucket][key][v.kind] = 0
                stats['values'][bucket][key][v.kind] += 1
            else:
                if stats['values'][bucket][key].get(v, None) is None:
                    stats['values'][bucket][key][v] = 0
                stats['values'][bucket][key][v] += 1


def stat_unknown(node, stats):
    _stat_default('unknown', node, stats)


def stat_default(node, stats):
    _stat_default(node.kind, node, stats)


def stat_word(node, stats):
    stat_default(node, stats)


def stat_redirect(node, stats):
    stat_default(node, stats)


def stat_assignment(node, stats):
    stat_default(node, stats)
    if stats['values'][node.kind].get('parts count', None) is None:
        stats['values'][node.kind]['parts count'] = {}
    parts_count = len(node.parts)
    if stats['values'][node.kind]['parts count'].get(parts_count, None) is None:
        stats['values'][node.kind]['parts count'][parts_count] = 0
    stats['values'][node.kind]['parts count'][parts_count] += 1

    if parts_count > 1:
        print(node)


def stat_compound(node, stats):
    stat_default(node, stats)


def stat_command(node, stats):
    stat_default(node, stats)


def stat_list(node, stats):
    stat_default(node, stats)


def stat_reservedword(node, stats):
    stat_default(node, stats)


def stat_operator(node, stats):
    stat_default(node, stats)


def stat_for(node, stats):
    stat_default(node, stats)


def stat_function(node, stats):
    stat_default(node, stats)


def stat_if(node, stats):
    stat_default(node, stats)


def stat_pipeline(node, stats):
    stat_default(node, stats)


def stat_pipe(node, stats):
    stat_default(node, stats)


def stat_parameter(node, stats):
    stat_default(node, stats)


def stat_commandsubstitution(node, stats):
    stat_default(node, stats)


def stat_tilde(node, stats):
    stat_default(node, stats)


def stat_while(node, stats):
    stat_default(node, stats)


def stat_until(node, stats):
    stat_default(node, stats)


def stat_heredoc(node, stats):
    stat_default(node, stats)


def stat_processsubstitution(node, stats):
    stat_default(node, stats)
