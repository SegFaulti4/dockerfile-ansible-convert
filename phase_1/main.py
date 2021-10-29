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
DIRECTIVE_PROCESSING = {cmd: getattr(process_directive, 'process_' + cmd) for cmd in VALID_DIRECTIVES}


def process(parsed, source_name):
    try:
        dockerfile_ast = {
            'type': 'DOCKER-FILE',
            'children': [],
            'source_name': source_name
        }

        # Check directives
        for directive in parsed:
            cmd = str(directive.cmd).lower()
            if cmd not in VALID_DIRECTIVES:
                raise InvalidDirectiveException(cmd)
            dockerfile_ast['children'].extend(DIRECTIVE_PROCESSING[cmd](directive))

        return json.dumps(dockerfile_ast, indent=4, sort_keys=True)

    except InvalidDirectiveException as id_ex:
        globalLog.warning(id_ex)
        return ''


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=False)
    arguments = parser.parse_args()
    return arguments


def handle_docker_str(string):
    return process(dockerfile.parse_string(string.strip()), 'str')


def handle_dockerfile(filepath):
    return process(dockerfile.parse_file(filepath.strip()), filepath)


def _write_processed_dockerfile(out_file, line, prefix=None):
    if prefix is None:
        prefix = ''

    globalLog.info('Reading from ' + line)
    try:
        out_file.write(prefix + handle_dockerfile(line))
    except Exception as ex:
        globalLog.warning(ex)
        pass


if __name__ == '__main__':
    args = parse_arguments()

    out_file = sys.stdout
    if args.file:
        try:
            out_file = open(args.file, 'w', newline='')
        except OSError as os_ex:
            globalLog.warning(os_ex)
            globalLog.info("Redirect file output into stdout")

    out_file.write('[')
    line = sys.stdin.readline()
    _write_processed_dockerfile(out_file=out_file, line=line, prefix='')
    for line in sys.stdin:
        _write_processed_dockerfile(out_file=out_file, line=line, prefix=',\n')
    out_file.write(']\n')
