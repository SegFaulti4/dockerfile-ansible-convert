import json
import dockerfile
import sys
import argparse
import logging
import phase_1.process_directive

from exception import ConvertException
from log import globalLog

globalLog.setLevel(logging.INFO)


class InvalidDirectiveException(ConvertException):
    pass


VALID_DIRECTIVES = [*dockerfile.all_cmds()]
DIRECTIVE_PROCESSING = {cmd: getattr(phase_1.process_directive, 'process_' + cmd) for cmd in VALID_DIRECTIVES}


def parse_dockerfile_from_path(filepath):
    return dockerfile.parse_file(filepath.strip())


def phase_1_process(parsed_dockerfile, meta_info):
    try:
        dockerfile_ast = {
            'type': 'DOCKER-FILE',
            'children': [],
            'meta_info': meta_info
        }

        # Check directives
        for directive in parsed_dockerfile:
            cmd = str(directive.cmd).lower()
            if cmd not in VALID_DIRECTIVES:
                raise InvalidDirectiveException(cmd)
            dockerfile_ast['children'].extend(DIRECTIVE_PROCESSING[cmd](directive))

        return dockerfile_ast

    except InvalidDirectiveException as id_ex:
        globalLog.warning(id_ex)
        return ''


def phase_1_obj_from_path(filepath):
    return phase_1_process(parsed_dockerfile=parse_dockerfile_from_path(filepath),
                           meta_info=filepath)


def dump_phase_1_obj(out_stream, obj, prefix=None):
    if prefix is None:
        prefix = ''

    try:
        out_stream.write(prefix + json.dumps(obj, indent=4, sort_keys=True))
    except Exception as ex:
        globalLog.warning(ex)
        pass


def dump_phase_1(in_stream, out_stream):
    out_stream.write('[')
    line = in_stream.readline()
    dump_phase_1_obj(out_stream=out_stream, obj=phase_1_obj_from_path(line), prefix='')
    for line in in_stream:
        dump_phase_1_obj(out_stream=out_stream, obj=phase_1_obj_from_path(line), prefix=',\n')
    out_stream.write(']\n')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=False)
    arguments = parser.parse_args()
    return arguments


def main():
    args = parse_arguments()

    out_stream = sys.stdout
    if args.file:
        try:
            out_stream = open(args.file, 'w', newline='')
        except OSError as os_ex:
            globalLog.warning(os_ex)
            globalLog.info("Redirect file output into stdout")
            out_stream = sys.stdout

    dump_phase_1(sys.stdin, out_stream)


if __name__ == '__main__':
    main()
