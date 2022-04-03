from exception import DockerfileStackException


class AnsibleStack(object):
    global_vars = dict()
    local_vars = dict()

    @staticmethod
    def fact2var(name):
        return name[:-5]

    @staticmethod
    def var2fact(name):
        return name + '_fact'

    def _global_var_value(self, name):
        return '{{ ' + self.var2fact(name) + ' }}'

    def _local_var_value(self, name):
        value_obj = self.local_vars[name]
        if value_obj['type'] == 'STRING-CONSTANT':
            return value_obj['value']
        else:
            return '{{ ' + value_obj['register'] + ' }}'

    def var_value(self, name):
        if self.local_vars.get(name, None) is None:
            if self.global_vars.get(name, None) is None:
                raise DockerfileStackException('Variable ' + name + ' is not found in either stack')
            else:
                return self._global_var_value(name)
        else:
            return self._local_var_value(name)

    def resolve_bash_word_with_context(self, obj):
        if obj['type'] == 'BASH-WORD':
            return obj['value']
        elif obj['type'] == 'BASH-WORD-PARAMETERIZED':
            params = [child for child in obj['children']]
            params.sort(key=lambda x: x['pos'][0], reverse=False)

            res = obj['value'][0:params[0]['pos'][0]] + self.var_value(params[0]['name'])
            for i in range(1, len(params)):
                res += obj['value'][params[i - 1]['pos'][1]:params[i]['pos'][0]] + self.var_value(params[i]['name'])
            res += obj['value'][params[-1]['pos'][1]:]

            return res

    def get_context(self):
        var_names = set([name for name in self.global_vars] + [name for name in self.local_vars])
        context = {name: self.var_value(name) for name in var_names}
        return context


def _bool_opt_value_is_true(command, opt_name):
    # may check for PARAMETERIZED-WORD with only STRING-CONSTANTs as well
    opt_val = command['options'].get(opt_name, False)
    if opt_val and opt_val['type'] == 'BASH-WORD' and opt_val['value'] == 'yes':
        opt_val = True
    return opt_val
