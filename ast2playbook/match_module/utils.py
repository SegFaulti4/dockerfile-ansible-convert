def _bool_opt_value_is_true(command, opt_name):
    opt_val = command['options'].get(opt_name, False)
    if opt_val and opt_val['type'] == 'BASH-WORD' and opt_val['value'] == 'yes':
        opt_val = True
    return opt_val
