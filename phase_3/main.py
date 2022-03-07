import sys
import argparse
import json
import logging

from phase_3 import enrich
import exception
from log import globalLog

globalLog.setLevel(logging.DEBUG)


BASH_PARAMETERIZED_WORD_CLASSES = ['local', 'global', 'untracked']
ENRICHED_COMMAND_CHILDREN_TYPES = ['BASH-WORD', 'BASH-PARAMETERIZED-WORD']


class Global:
    stack = set()
    directive_stack = set()


def load_phase_2(in_stream):
    return json.load(in_stream)


def phase_3_enrich_command(obj):
    return enrich.enrich_command(obj, global_stack=Global.stack, local_stack=Global.directive_stack)


def _enrich_command_is_applicable(comm):
    return comm['children'][0]['type'] == 'BASH-WORD' and \
        all(x['type'] == 'BASH-WORD' or x['type'] == 'BASH-PARAMETERIZED-WORD' and x['class'] != 'untracked'
            for x in comm['children'])


def phase_3_ast_visit(obj):
    if obj['type'] == 'DOCKER-ENV':
        Global.stack.add(obj['name'])
    elif obj['type'] == 'DOCKER-RUN':
        Global.directive_stack = set()
        for i in range(len(obj['children'])):
            obj['children'][i] = phase_3_ast_visit(obj['children'][i])
    elif obj['type'] == 'BASH-COMMAND':
        # TODO: check for assignments and export
        for parameterized in filter(lambda x: x['type'] == 'BASH-PARAMETERIZED-WORD', obj['children']):
            class_flag = 0
            for param in filter(lambda x: x['type'] == 'BASH-PARAMETER', parameterized['children']):
                if param['value'] in Global.directive_stack:
                    param['type'] = 'LOCAL-BASH-PARAMETER'
                elif param['value'] in Global.stack:
                    class_flag = max(class_flag, 1)
                    param['type'] = 'GLOBAL-BASH-PARAMETER'
                else:
                    class_flag = max(class_flag, 2)
                    param['type'] = 'UNTRACKED-BASH-PARAMETER'
            parameterized['class'] = BASH_PARAMETERIZED_WORD_CLASSES[class_flag]

        if _enrich_command_is_applicable(obj):
            obj = phase_3_enrich_command(obj)
    else:
        if obj.get('children', None) is not None:
            if len(obj['children']):
                for i in range(len(obj['children'])):
                    obj['children'][i] = phase_3_ast_visit(obj['children'][i])
    return obj


def phase_3_process(obj):
    Global.stack = set()
    return phase_3_ast_visit(obj)


def dump_phase_3_obj(out_stream, obj, prefix=None):
    if prefix is None:
        prefix = ''

    globalLog.info('Phase 3 of dockerfile, meta_info: ' + obj['meta_info'])
    try:
        out_stream.write(prefix + json.dumps(obj, indent=4, sort_keys=True))
    except Exception as ex:
        globalLog.warning(ex)
        pass


def dump_phase_3(in_stream, out_stream):
    ph_2 = load_phase_2(in_stream)
    out_stream.write('[')
    dump_phase_3_obj(out_stream=out_stream, obj=phase_3_process(ph_2[0]), prefix='')
    for ph_2_obj in ph_2[1:]:
        dump_phase_3_obj(out_stream=out_stream, obj=phase_3_process(ph_2_obj), prefix=',\n')
    out_stream.write(']\n')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=False)
    arguments = parser.parse_args()
    return arguments


def main():
    args = parse_arguments()
    enrich.init_commands_config()

    out_stream = sys.stdout
    if args.file:
        try:
            out_stream = open(args.file, 'w', newline='')
        except OSError as os_ex:
            out_stream = sys.stdout
            globalLog.warning(os_ex)
            globalLog.info("Redirect file output into stdout")

    dump_phase_3(open("./dataset/phase_2.json", 'r'), out_stream)


if __name__ == '__main__':
    main()
