import json
import dockerfile
import sys
import argparse
import process_directive

from exception import ConvertException
from log import globalLog


class InvalidDirectiveException(ConvertException):
    pass


VALID_DIRECTIVES = [*dockerfile.all_cmds()]


def process(item):
    directive_processing = {cmd: getattr(process_directive, 'process_' + cmd) for cmd in VALID_DIRECTIVES}

    try:
        parsed = item

        dockerfile_ast = {
            'type': 'DOCKER-FILE',
            'children': []
        }

        # Check directives
        for directive in parsed:
            cmd = str(directive.cmd).lower()
            if cmd not in VALID_DIRECTIVES:
                raise InvalidDirectiveException(cmd)
            dockerfile_ast['children'].extend(directive_processing[cmd](directive))

        return json.dumps(dockerfile_ast, indent=4, sort_keys=True)

    except InvalidDirectiveException as id_ex:
        globalLog.warning(id_ex)
        return ''


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=False)
    arguments = parser.parse_args()
    return arguments


def handle_str(string):
    return process(dockerfile.parse_string(string.strip()))


def handle_dockerfile(filepath):
    return process(dockerfile.parse_file(filepath.strip()))


if __name__ == '__main__':
    args = parse_arguments()

    out_file = sys.stdout
    if args.file:
        try:
            out_file = open(args.file, 'w')
        except OSError as os_ex:
            globalLog.warning(os_ex)
            globalLog.info("Redirect file output into stdout")

    for line in sys.stdin:
        globalLog.info('Reading from ' + line)
        try:
            out_file.write(handle_dockerfile(line) + '\n')
        except Exception as ex:
            globalLog.warning(ex)
            continue
