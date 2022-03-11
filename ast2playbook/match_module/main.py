from ast2playbook.match_module.match_apt_get import match_apt_get
from ast2playbook.match_module.utils import _bool_opt_value_is_true

from exception import MatchAnsibleModuleException


def default_match(command):
    return {
        'shell': {
            'cmd': command['line']
        }
    }


def match_rm(command):
    if _bool_opt_value_is_true(command, '-r') and _bool_opt_value_is_true(command, '-f'):
        return {
            'ansible.builtin.file': {
                'path': command['paths'],
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
        return default_match(command)
    else:
        raise MatchAnsibleModuleException('Unknown command name ' + command['name'])
