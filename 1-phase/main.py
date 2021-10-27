import json
import dockerfile
import sys
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

        return json.dumps(dockerfile_ast)

    except InvalidDirectiveException as id_ex:
        globalLog.warning(id_ex)
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
