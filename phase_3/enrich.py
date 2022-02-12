import glob
import os
import yaml
import exception
from log import globalLog

commands_config = {}


def init_commands_config():
    path = './dataset/commands/'
    for filename in glob.glob(os.path.join(path, '*.yml')):
        with open(os.path.join(os.getcwd(), filename), 'r') as _f:  # open in readonly mode
            try:
                commands_config[filename[len(path):filename.find('.yml')]] = yaml.safe_load(_f)
            except yaml.YAMLError as exc:
                globalLog.warning(exc)
                continue


def _scenario_word_is_optional_abstraction_list(s):
    if s[0] == '[' and len(s) >= 5 and s[-4:] == '...]':
        return True
    return False


def _scenario_word_is_optional_abstraction(s):
    if s[0] == '[' and s[-1] == ']' and (len(s) < 5 or s[-4:] != '...]'):
        return True
    return False


def _scenario_word_is_required_abstraction(s):
    if s[0] == '<' and s[-1] == '>':
        return True
    return False


def _scenario_word_is_abstract(s):
    if _scenario_word_is_required_abstraction(s) or \
            _scenario_word_is_optional_abstraction_list(s) or \
            _scenario_word_is_optional_abstraction(s):
        return True
    return False


def _scenario_abstract_word_name(s):
    if _scenario_word_is_required_abstraction(s):
        return s[1:-1]
    if _scenario_word_is_optional_abstraction(s):
        return s[1:-1]
    if _scenario_word_is_optional_abstraction_list(s):
        return s[1:-4]


def _scenario_long_opt_name(s):
    if s.find('=') != -1:
        return s[s.find('--'):s.find('=')]
    return s[s.find('--'):]


def _scenario_short_opt_name(s):
    if s.find('=') != -1:
        return s[s.find('-'):s.find('=')]
    if s.find(',') != -1:
        return s[s.find('-'):s.find(',')]
    return s[s.find('-'):]


def _scenario_opt_obtain_str_value(comm_list, full_value):
    eq_pos = full_value.find('=')
    if eq_pos != -1:
        if eq_pos + 1 >= len(full_value):
            opt_value = ''
        else:
            opt_value = full_value[eq_pos + 1:]
    else:
        if len(comm_list) == 0 or comm_list[0][0] == '-':
            opt_value = ''
        else:
            opt_value = comm_list.pop(0)
    return opt_value


def _scenario_fit_opt_type_values(comm_list, fitted_options, fitted_opt, full_value):
    fitted_options[fitted_opt] = True


def _scenario_fit_opt_type_strings(comm_list, fitted_options, fitted_opt, full_value):
    opt_value = _scenario_opt_obtain_str_value(comm_list, full_value)
    fitted_options[fitted_opt] = opt_value


def _scenario_fit_opt_type_paths(comm_list, fitted_options, fitted_opt, full_value):
    opt_value = _scenario_opt_obtain_str_value(comm_list, full_value)
    if opt_value == '':
        raise exception.EnrichCommandException('Path option value is not provided')
    fitted_options[fitted_opt] = opt_value


def _scenario_fit_opt_type_counts(comm_list, fitted_options, fitted_opt, full_value):
    eq_pos = full_value.find('=')
    if eq_pos == -1:
        if fitted_options.get(fitted_opt, None) is None:
            fitted_options[fitted_opt] = 1
        else:
            fitted_options[fitted_opt] += 1
    else:
        if eq_pos + 1 >= len(full_value):
            fitted_options[fitted_opt] = 0
        else:
            fitted_options[fitted_opt] = int(full_value[eq_pos + 1:])


def _scenario_fit_opt_type_arrays(comm_list, fitted_options, fitted_opt, full_value):
    opt_value = _scenario_opt_obtain_str_value(comm_list, full_value)
    if fitted_options.get(fitted_opt, None) is None:
        fitted_options[fitted_opt] = list()
    fitted_options[fitted_opt].append(opt_value)


def _scenario_explode_option_list(comm_list):
    if comm_list[0][0:2] == '--':
        values = [comm_list[0]]
    else:
        if comm_list[0].find('=') != -1:
            values = [comm_list[0]]
        else:
            values = ['-' + ch for ch in _scenario_short_opt_name(comm_list[0])[1:]]
            comm_list.pop(0)
            for value in values:
                comm_list.insert(0, value)
    return values


def _scenario_fit_option(scenario, comm_list, node):
    values = _scenario_explode_option_list(comm_list)

    for full_value in values:
        if full_value[0:2] == '--':
            value = _scenario_long_opt_name(full_value)
        else:
            value = _scenario_short_opt_name(full_value)

        fitted_opt = None
        fitted_opt_type = None
        for opt_type in scenario['options']:
            for opt in scenario['options'][opt_type]:
                if value[0:2] == '--':
                    tmp_opt = _scenario_long_opt_name(opt)
                else:
                    tmp_opt = _scenario_short_opt_name(opt)
                if tmp_opt == value:
                    fitted_opt = tmp_opt
                    fitted_opt_type = opt_type
                    break

        if fitted_opt is None:
            raise exception.EnrichCommandException('Unknown option ' + value)

        comm_list.pop(0)
        if fitted_opt_type == 'booleans':
            _scenario_fit_opt_type_values(comm_list, node['options'], fitted_opt, full_value)
        elif fitted_opt_type == 'strings':
            _scenario_fit_opt_type_strings(comm_list, node['options'], fitted_opt, full_value)
        elif fitted_opt_type == 'paths':
            _scenario_fit_opt_type_paths(comm_list, node['options'], fitted_opt, full_value)
        elif fitted_opt_type == 'counts':
            _scenario_fit_opt_type_counts(comm_list, node['options'], fitted_opt, full_value)
        elif fitted_opt_type == 'arrays':
            _scenario_fit_opt_type_arrays(comm_list, node['options'], fitted_opt, full_value)
        else:
            raise exception.EnrichCommandException('Opt type not implemented ' + fitted_opt_type)


def _scenario_is_suitable(scenario, comm, name):
    try:
        node = {'type': 'ENRICHED-COMMAND', 'name': name, 'full name': scenario['name'], 'options': dict(),
                'line': comm['line']}
        cmd = scenario['cmd'].split()
        comm_list = [child['value'] for child in comm['children']]
        comm_list.pop(0)
        accepting_command_options = True

        for i in range(1, len(cmd)):
            if not _scenario_word_is_abstract(cmd[i]):
                if comm_list[0] != cmd[i]:
                    return None
                comm_list.pop(0)
            else:
                while len(comm_list) and accepting_command_options and comm_list[0][0] == '-':
                    if comm_list[0] == '--':
                        comm_list.pop(0)
                        accepting_command_options = False
                        break
                    _scenario_fit_option(scenario, comm_list, node)
                if _scenario_word_is_required_abstraction(cmd[i]):
                    if len(comm_list) == 0:
                        raise exception.EnrichCommandException('Required argument is not provided')
                    node[_scenario_abstract_word_name(cmd[i])] = comm_list.pop(0)
                elif _scenario_word_is_optional_abstraction(cmd[i]):
                    if len(comm_list):
                        node[_scenario_abstract_word_name(cmd[i])] = comm_list.pop(0)
                elif _scenario_word_is_optional_abstraction_list(cmd[i]):
                    while len(comm_list) > 0:
                        if accepting_command_options and comm_list[0][0] == '-':
                            _scenario_fit_option(scenario, comm_list, node)
                        else:
                            if node.get(_scenario_abstract_word_name(cmd[i]), None) is None:
                                node[_scenario_abstract_word_name(cmd[i])] = []
                            node[_scenario_abstract_word_name(cmd[i])].append(comm_list.pop(0))

        # to fit options in the end of command
        while len(comm_list) and accepting_command_options and comm_list[0][0] == '-':
            if comm_list[0] == '--':
                comm_list.pop(0)
                break
            _scenario_fit_option(scenario, comm_list, node)

        if len(comm_list):
            raise exception.EnrichCommandException('Excessive arguments provided')
        return node

    except ValueError as exc:
        globalLog.info(exc)
        return None
    except KeyError as exc:
        globalLog.info(exc)
        return None
    except exception.EnrichCommandException as exc:
        globalLog.info(exc)
        globalLog.info(comm['line'])
        return None


def enrich_command(comm):
    if len(comm['children']) == 0:
        return comm
    if comm['children'][0]['type'] != 'BASH-WORD' or commands_config.get(comm['children'][0]['value'], None) is None:
        return comm
    else:
        conf = commands_config[comm['children'][0]['value']]['command']
        suitable_scenarios = conf['scenarios'].copy()
        for scenario in suitable_scenarios:
            scenario_res = _scenario_is_suitable(scenario, comm, conf['name'])
            if scenario_res is not None:
                return scenario_res
        globalLog.warning("Suitable scenario not found for command " + comm['line'])
        return comm
