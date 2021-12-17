import argparse
import json
import sys
import logging

import bashlex
from bashlex.errors import ParsingError

import exception
from log import globalLog
from parse_bashlex import parse_bashlex_node

globalLog.setLevel(logging.DEBUG)


# BASHLEX_IMPLEMENTED_NODES = ['list', 'command', 'operator', 'word', 'parameter']
# BASHLEX_NODE_PARSING = {node_kind: getattr(parse_bashlex, 'parse_bashlex_' + node_kind)
#                         for node_kind in BASHLEX_IMPLEMENTED_NODES}


def load_phase_1(in_stream):
    return json.load(in_stream)


def parse_bash_with_bashlex(bash_line):
    parts = None
    res = None
    try:
        parts = bashlex.parse(bash_line)
        res = parse_bashlex_node(parts[0], bash_line)
    except exception.BashlexParsingException as exc:
        globalLog.info(exc)
        globalLog.info('Bashlex AST parsing failed for AST: ' + str(parts))
    except (ParsingError, NotImplementedError) as exc:
        globalLog.info(exc)
        globalLog.info('Bash parsing failed for line: ' + bash_line)
    except Exception as exc:
        globalLog.warning(type(exc))
        globalLog.warning(exc)
        globalLog.warning(bash_line)
    finally:
        return res


def phase_2_ast_visit(obj):
    if obj['type'] == 'MAYBE-BASH':
        res = parse_bash_with_bashlex(obj['value'])
        if res is None:
            globalLog.info(obj['type'] + ' node is untouched')
            return obj
        else:
            return res
    else:
        if len(obj['children']):
            for i in range(len(obj['children'])):
                obj['children'][i] = phase_2_ast_visit(obj['children'][i])
    return obj


def phase_2_process(obj):
    return phase_2_ast_visit(obj)


def dump_phase_2_obj(out_stream, obj, prefix=None):
    if prefix is None:
        prefix = ''

    globalLog.info('Phase 2 of dockerfile, meta_info: ' + obj['meta_info'])
    try:
        out_stream.write(prefix + json.dumps(obj, indent=4, sort_keys=True))
    except Exception as ex:
        globalLog.warning(ex)
        pass


def dump_phase_2(in_stream, out_stream):
    ph_1 = load_phase_1(in_stream)
    out_stream.write('[')
    dump_phase_2_obj(out_stream=out_stream, obj=phase_2_process(ph_1[0]), prefix='')
    for ph_1_obj in ph_1[1:]:
        dump_phase_2_obj(out_stream=out_stream, obj=phase_2_process(ph_1_obj), prefix=',\n')
    out_stream.write(']\n')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=False)
    arguments = parser.parse_args()
    return arguments


if __name__ == '__main__':
    args = parse_arguments()

    out_stream = sys.stdout
    if args.file:
        try:
            out_stream = open(args.file, 'w', newline='')
        except OSError as os_ex:
            out_stream = sys.stdout
            globalLog.warning(os_ex)
            globalLog.info("Redirect file output into stdout")

    dump_phase_2(sys.stdin, out_stream)
