from docker2ansible.ast2playbook.ansible_stack import _bool_opt_value_is_true
from docker2ansible.ast2playbook.apt_get_matcher import AptGetMatcher
from docker2ansible.exception import MatchAnsibleModuleException


class ModuleMatcher:

    def __init__(self, stack):
        self.stack = stack
        self.apt_get_matcher = AptGetMatcher(self.stack)

    @staticmethod
    def default_match(command):
        return {
            'shell': {
                'cmd': command['line']
            }
        }

    def match_rm(self, command):
        if _bool_opt_value_is_true(command, '-r') and _bool_opt_value_is_true(command, '-f'):
            return {
                'ansible.builtin.file': {
                    'path': [self.stack.resolve_bash_word_with_context(word) for word in command['paths']],
                    'state': 'absent'
                }
            }
        else:
            return self.default_match(command)

    def match_ansible_module(self, command):
        if command['name'] == 'rm':
            return self.match_rm(command)
        elif command['name'] == 'echo':
            return self.default_match(command)
        elif command['name'] == 'apt-get':
            return self.default_match(command)
        else:
            raise MatchAnsibleModuleException('Unknown command name ' + command['name'])
