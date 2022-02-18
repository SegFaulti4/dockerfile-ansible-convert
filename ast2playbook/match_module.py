from match_apt_get import match_apt_get
from main import globalLog
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


def match_ansible_module(command):
    if command['name'] == 'rm':
        return match_rm(command)
    elif command['name'] == 'echo':
        return default_match(command)
    elif command['name'] == 'apt-get':
        return match_apt_get(command)
    else:
        raise MatchAnsibleModuleException('Unknown command name ' + command['name'])
