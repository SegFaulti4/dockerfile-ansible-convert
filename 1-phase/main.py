import process_directive
import json

VALID_DIRECTIVES = [
    'from',
    'run',
    'cmd',
    'label',
    'maintainer',
    'expose',
    'env',
    'add',
    'copy',
    'entrypoint',
    'volume',
    'user',
    'workdir',
    'arg',
    'onbuild',
    'stopsignal',
    'healthcheck',
    'shell'
]


def process(item):
    directive_processing = {cmd: getattr(process_directive, 'process_' + cmd) for cmd in VALID_DIRECTIVES}

    try:
        parsed = item[0]

        dockerfile_ast = {
            'type': 'DOCKER-FILE',
            'children': []
        }

        # Check directives
        for directive in parsed:
            cmd = directive.cmd
            if cmd not in VALID_DIRECTIVES:
                # Not valid dockerfile
                raise Exception('found invalid directive {}'.format(cmd))
            dockerfile_ast['children'].extend(directive_processing[cmd](directive))

        dockerfile_ast['file_sha'] = item[1].split('/')[-1].replace(
            '.Dockerfile', ''
        ).strip()

        return json.dumps(dockerfile_ast)

    except Exception as ex:
        return None
