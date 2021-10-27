import json
import logging
import dockerfile
import sys
import process_directive


# TODO: import this from module
class ConvertException(Exception):
    pass


class InvalidDirectiveException(ConvertException):
    pass


# TODO: import this from module
globalLog = logging.getLogger('global')
globalLog.setLevel(logging.INFO)

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
                # Not valid dockerfile
                raise InvalidDirectiveException(cmd)
            dockerfile_ast['children'].extend(directive_processing[cmd](directive))

        return json.dumps(dockerfile_ast)

    except InvalidDirectiveException as ex:
        globalLog.warning(ex)
        return ''


if __name__ == '__main__':
    with open(sys.argv[1], mode='w') as out_f:
        for line in sys.stdin:
            globalLog.info(line)
            try:
                out_f.write(process(dockerfile.parse_file(line.strip())))
            except Exception as ex:
                globalLog.warning(ex)
                continue
