from exception import MatchAnsibleModuleException


def default_match(command):
    return {
        'shell': {
            'cmd': command['line']
        }
    }


def match_rm(command):
    if command['options'].get('-f', False) and command['options'].get('-r', False):
        return {
            'ansible.builtin.file': {
                'path': [command['paths']],
                'state': 'absent'
            }
        }
    else:
        return default_match(command)


def match_apt_get(command):
    res = dict()
    # general flags match
    res['force-apt-get'] = 'yes'

    if command['options'].pop('--force-yes', False) or (
        command['options'].pop('--allow-unauthenticated', False) and
        command['options'].pop('--allow-downgrades', False) and
        command['options'].pop('--allow-remove-essential', False) and
        command['options'].pop('--allow-change-held-packages', False)
    ):
        res['force'] = 'yes'
    if command['options'].pop('--allow-unauthenticated', False):
        res['allow_unauthenticated'] = 'yes'
    if command['options'].pop('-t', False) or command['options'].pop('--target-release', False):
        res['default_release'] = 'yes'
    if command['options'].pop('--no-install-recommends', False):
        res['install_recommends'] = 'no'

    if command['full name'] == 'apt-get install':
        pass
    return None


def match_ansible_module(command):
    if command['name'] == 'rm':
        return match_rm(command)
    elif command['name'] == 'echo':
        return default_match(command)
    elif command['name'] == 'apt-get':
        return match_apt_get(command)
    else:
        raise MatchAnsibleModuleException('Unknown command name ' + command['name'])
