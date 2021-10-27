def process_from(directive):
    res = {
        'type': 'DOCKER-FROM',
        'children': []
    }

    value = directive.value[0]
    name = value.split('/')[-1].strip() if '/' in value else value
    name = name.split(':')[0].strip() if ':' in name else name

    res['children'].append({
        'type': 'DOCKER-IMAGE-NAME',
        'value': name,
        'children': []
    })

    if '/' in value:
        res['children'].append({
            'type': 'DOCKER-IMAGE-REPO',
            'value': value.split('/')[0].strip(),
            'children': []
        })

    if ':' in value:
        res['children'].append({
            'type': 'DOCKER-IMAGE-TAG',
            'value': value.split(':')[-1].strip() if ':' in value else None,
            'children': []
        })

    return [res]


def process_run(directive):
    return [{
        'type': 'DOCKER-RUN',
        'children': [{
            'type': 'MAYBE-BASH',
            'value': directive.value[0],
            'children': []
        }]
    }]


def process_cmd(directive):
    res = {
        'type': 'DOCKER-CMD',
        'children': []
    }

    for value in directive.value:
        res['children'].append({
            'type': 'DOCKER-CMD-ARG',
            'value': value,
            'children': []
        })

    return [res]


def process_label(directive):
    return []


def process_maintainer(directive):
    return []


def process_expose(directive):
    return [{
        'type': 'DOCKER-EXPOSE',
        'children': [{
            'type': 'DOCKER-PORT',
            'value': directive.value[0],
            'children': []
        }]
    }]


def process_env(directive):
    return [
        {
            'type': 'DOCKER-ENV',
            'children': [
                {'type': 'DOCKER-NAME', 'value': name, 'children': []},
                {'type': 'DOCKER-LITERAL', 'value': value, 'children': []}
            ]
        }
        for name, value in zip(directive.value[::2], directive.value[1::2])
    ]


def process_add(directive):
    res = {
        'type': 'DOCKER-ADD',
        'children': []
    }

    res['children'].append({
        'type': 'DOCKER-ADD-TARGET',
        'children': [{
            'type': 'DOCKER-PATH',
            'value': directive.value[-1],
            'children': []
        }]
    })

    for arg in directive.value[:-1]:
        res['children'].append({
            'type': 'DOCKER-ADD-SOURCE',
            'children': [{
                'type': 'DOCKER-PATH',
                'value': arg,
                'children': []
            }]
        })

    return [res]


def process_copy(directive):
    res = {
        'type': 'DOCKER-COPY',
        'children': []
    }

    res['children'].append({
        'type': 'DOCKER-COPY-TARGET',
        'children': [{
            'type': 'DOCKER-PATH',
            'value': directive.value[-1],
            'children': []
        }]
    })

    for arg in directive.value[:-1]:
        res['children'].append({
            'type': 'DOCKER-COPY-SOURCE',
            'children': [{
                'type': 'DOCKER-PATH',
                'value': arg,
                'children': []
            }]
        })

    return [res]


def process_entrypoint(directive):
    first = directive.value[0]

    res = {
        'type': 'DOCKER-ENTRYPOINT',
        'children': [{
            'type': 'DOCKER-ENTRYPOINT-EXECUTABLE',
            'value': first,
            'children': []
        }]
    }

    for value in directive.value[1:]:
        res['children'].append({
            'type': 'DOCKER-ENTRYPOINT-ARG',
            'value': value,
            'children': []
        })

    return [res]


def process_volume(directive):
    return [
        {
            'type': 'DOCKER-VOLUME',
            'children': [{
                'type': 'DOCKER-PATH',
                'value': arg,
                'children': []
            }]
        }
        for arg in directive.value
    ]


def process_user(directive):
    return [{
        'type': 'DOCKER-USER',
        'children': [{
            'type': 'DOCKER-LITERAL',
            'value': directive.value[0],
            'children': []
        }]
    }]


def process_workdir(directive):
    return [{
        'type': 'DOCKER-WORKDIR',
        'children': [{
            'type': 'DOCKER-PATH',
            'value': directive.value[0],
            'children': []
        }]
    }]


def process_arg(directive):
    res = {
        'type': 'DOCKER-ARG',
        'children': [{
            'type': 'DOCKER-NAME',
            'value': directive.value[0] if '=' not in directive.value[0] else directive.value[0].split('=')[
                0].strip(),
            'children': []
        }]
    }

    if '=' in directive.value[0]:
        res['children'].append({
            'type': 'DOCKER-LITERAL',
            'value': directive.value[0].split('=')[-1].strip(),
            'children': []
        })

    return [res]


def process_onbuild(directive):
    return []


def process_stopsignal(directive):
    return []


def process_healthcheck(directive):
    return []


def process_shell(directive):
    first = directive.value[0]

    res = {
        'type': 'DOCKER-SHELL',
        'children': [{
            'type': 'DOCKER-SHELL-EXECUTABLE',
            'value': first,
            'children': []
        }]
    }

    for value in directive.value[1:]:
        res['children'].append({
            'type': 'DOCKER-SHELL-ARG',
            'value': value,
            'children': []
        })

    return [res]
