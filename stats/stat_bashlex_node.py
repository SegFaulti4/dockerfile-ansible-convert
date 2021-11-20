import exception
import sys
import logging

from log import globalLog
globalLog.setLevel(logging.INFO)


def stat_unknown(node, stats):
    stats['UNKNOWN']['values'].append(node)


def stat_default(node, stats):
    stats[node.kind]['values'].append(node)


def stat_word(node, stats):
    stat_default(node, stats)
    # if len(node.parts):
    #     stats[node.kind]['values'].append({'kind': node.kind, 'complexity': 'complex'})
    # else:
    #     stats[node.kind]['values'].append({'kind': node.kind, 'complexity': 'trivial'})


def stat_redirect(node, stats):
    stat_default(node, stats)
    # stats[node.kind]['values'].append({'kind': node.kind, 'type': node.type})


def stat_assignment(node, stats):
    stat_default(node, stats)


def stat_compound(node, stats):
    stat_default(node, stats)


def stat_command(node, stats):
    stat_default(node, stats)
    # stats[node.kind]['values'].append({'kind': node.kind})


def stat_list(node, stats):
    stat_default(node, stats)
    # stats[node.kind]['values'].append({'kind': node.kind})


def stat_reservedword(node, stats):
    stat_default(node, stats)


def stat_operator(node, stats):
    if stats[node.kind].get(node.op, None) is None:
        stats[node.kind][node.op] = 0
    stats[node.kind][node.op] += 1


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
