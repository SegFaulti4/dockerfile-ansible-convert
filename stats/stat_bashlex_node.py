import exception
import sys

from log import globalLog


def stat_unknown(node, stats):
    stats['UNKNOWN'].append(node)


def stat_default(node, stats):
    stats[node.kind].append(node)


def stat_word(node, stats):
    stat_default(node, stats)


def stat_redirect(node, stats):
    stat_default(node, stats)


def stat_assignment(node, stats):
    stat_default(node, stats)


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
