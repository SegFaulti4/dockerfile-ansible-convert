import glob
import os
import yaml
import exception
from log import globalLog

commands_config = {}


ENRICHED_COMMAND_CHILDREN_TYPES = ['BASH-WORD', 'BASH-WORD-PARAMETERIZED']


def init_commands_config():
    path = './dataset/commands/'
    for filename in glob.glob(os.path.join(path, '*.yml')):
        with open(os.path.join(os.getcwd(), filename), 'r') as _f:  # open in readonly mode
            try:
                commands_config[filename[len(path):filename.find('.yml')]] = yaml.safe_load(_f)
            except yaml.YAMLError as exc:
                globalLog.warning(exc)
                continue


def _scenario_word_is_an_optional_abstraction_list(s):
    if s[0] == '[' and len(s) >= 5 and s[-4:] == '...]':
        return True
    return False


def _scenario_word_is_an_optional_abstraction(s):
    if s[0] == '[' and s[-1] == ']' and (len(s) < 5 or s[-4:] != '...]'):
        return True
    return False


def _scenario_word_is_a_required_abstraction(s):
    if s[0] == '<' and s[-1] == '>':
        return True
    return False


def _scenario_word_is_abstract(s):
    if _scenario_word_is_a_required_abstraction(s) or \
            _scenario_word_is_an_optional_abstraction_list(s) or \
            _scenario_word_is_an_optional_abstraction(s):
        return True
    return False


def _scenario_abstract_word_name(s):
    if _scenario_word_is_a_required_abstraction(s):
        return s[1:-1]
    if _scenario_word_is_an_optional_abstraction(s):
        return s[1:-1]
    if _scenario_word_is_an_optional_abstraction_list(s):
        return s[1:-4]


def _scenario_long_opt_name(s):
    if s.find('=') != -1:
        return s[s.find('--'):s.find('=')]
    return s[s.find('--'):]


def _scenario_short_opt_name(s):
    if s.find('=') != -1:
        return s[s.find('-'):s.find('=')]
    return s[s.find('-'):]


def _scenario_opt_name(node):
    if node['value'][0:2] == '--':
        return _scenario_long_opt_name(node['value'])
    return _scenario_short_opt_name(node['value'])


def _scenario_opt_obtain_str_value(comm_list, new_option, listed_value=True):
    default_opt_value = {'type': 'BASH-WORD', 'value': ''}

    eq_pos = new_option['value'].find('=')
    if eq_pos != -1:
        if eq_pos + 1 >= len(new_option['value']):
            opt_value = default_opt_value
        else:
            opt_value = {
                'type': new_option['type'],
                'value': new_option['value'][eq_pos + 1:]
            }
            if new_option['type'] == 'BASH-WORD':
                pass
            elif new_option['type'] == 'BASH-WORD-PARAMETERIZED':
                opt_value['children'] = new_option['children'].copy()
                for child in opt_value['children']:
                    child['pos'] = (child['pos'][0] - eq_pos - 1, child['pos'][1] - eq_pos - 1)
            else:
                raise exception.EnrichCommandException(
                    'Unsupported node type for enriched command with string value option: ' + new_option['type']
                )
    else:
        if not listed_value or len(comm_list) == 0 or _bash_word_is_an_option(comm_list[0]):
            opt_value = default_opt_value
        else:
            opt_value = comm_list.pop(0)
    return opt_value


def _scenario_fit_opt_type_booleans(comm_list, node_options, new_option_name, new_option):
    opt_value = _scenario_opt_obtain_str_value(comm_list, new_option, listed_value=False)
    if not opt_value['value']:
        opt_value = {'type': 'BASH-WORD', 'value': 'yes'}
    elif opt_value['value'] == 'yes' or opt_value['value'] == 'no':
        pass
    else:
        globalLog.warning('Unexpected value for boolean option: ' + str(new_option))
    node_options[new_option_name] = opt_value


def _scenario_fit_opt_type_strings(comm_list, node_options, new_option_name, new_option):
    opt_value = _scenario_opt_obtain_str_value(comm_list, new_option)
    node_options[new_option_name] = opt_value


def _scenario_fit_opt_type_paths(comm_list, node_options, new_option_name, new_option):
    opt_value = _scenario_opt_obtain_str_value(comm_list, new_option)
    if opt_value == '':
        raise exception.EnrichCommandException('Path option value is not provided')
    node_options[new_option_name] = opt_value


def _scenario_fit_opt_type_counts(comm_list, node_options, new_option_name, new_option):
    opt_value = _scenario_opt_obtain_str_value(comm_list, new_option, listed_value=False)
    if not opt_value['value']:
        if node_options.get(new_option_name, None) is None:
            node_options[new_option_name] = {'type': 'BASH-WORD', 'value': '1'}
        elif node_options[new_option_name]['type'] == 'BASH-WORD':
            node_options[new_option_name]['value'] = str(int(node_options[new_option_name]['value']) + 1)
        elif node_options[new_option_name]['type'] == 'BASH-WORD-PARAMETERIZED':
            node_options[new_option_name]['value'] = node_options[new_option_name]['value'] + ' + 1'
        else:
            raise exception.EnrichCommandException(
                'Unsupported node type for enriched command with count option: ' + new_option['type']
            )
    else:
        node_options[new_option_name] = opt_value


def _scenario_fit_opt_type_arrays(comm_list, node_options, new_option_name, new_option):
    opt_value = _scenario_opt_obtain_str_value(comm_list, new_option)
    if node_options.get(new_option_name, None) is None:
        node_options[new_option_name] = list()
    node_options[new_option_name].append(opt_value)


def _scenario_explode_option_list(comm_list):
    if comm_list[0]['value'][0:2] == '--':
        values = [comm_list[0]]
    else:
        if comm_list[0]['value'].find('=') != -1:
            values = [comm_list[0]]
        else:
            # No parameterized words here
            values = [{'type': 'BASH-WORD', 'value': '-' + ch} for ch in _scenario_opt_name(comm_list[0])[1:]]
            comm_list.pop(0)
            for value in values:
                comm_list.insert(0, value)
    return values


def _scenario_fit_opt_type(comm_list, node_options, new_option_name, new_option_type, new_option):
    if new_option_type == 'booleans':
        _scenario_fit_opt_type_booleans(comm_list, node_options, new_option_name, new_option)
    elif new_option_type == 'strings':
        _scenario_fit_opt_type_strings(comm_list, node_options, new_option_name, new_option)
    elif new_option_type == 'paths':
        _scenario_fit_opt_type_paths(comm_list, node_options, new_option_name, new_option)
    elif new_option_type == 'counts':
        _scenario_fit_opt_type_counts(comm_list, node_options, new_option_name, new_option)
    elif new_option_type == 'arrays':
        _scenario_fit_opt_type_arrays(comm_list, node_options, new_option_name, new_option)
    else:
        raise exception.EnrichCommandException('Option type is not implemented ' + new_option_type)


def _scenario_fit_option(scenario, comm_list, node):
    option_list = _scenario_explode_option_list(comm_list)

    for option in option_list:
        option_name = _scenario_opt_name(option)
        fitted_opt = None
        fitted_opt_type = None
        for opt_type in scenario['options']:
            for opt in scenario['options'][opt_type]:
                if opt == option_name:
                    fitted_opt = opt
                    fitted_opt_type = opt_type
                    break

        if fitted_opt is None:
            raise exception.EnrichCommandException('Unknown option ' + option_name)

        comm_list.pop(0)
        _scenario_fit_opt_type(comm_list=comm_list, node_options=node['options'], new_option_name=fitted_opt,
                               new_option_type=fitted_opt_type, new_option=option)


def _bash_word_is_an_option(node):
    if node['value'][0] == '-':
        if node['type'] == 'BASH-WORD':
            return True
        elif node['type'] == 'BASH-WORD-PARAMETERIZED':
            eq_pos = node['value'].find('=')
            min_param_pos = min(map(lambda x: x['pos'][0], node['children']))
            if min_param_pos > eq_pos > 1:
                return True
            return False
        else:
            raise exception.EnrichCommandException('Unsupported node type for enriched command: ' + node['type'])
    return False


def _bash_word_is_a_skip_word(node):
    return node['value'] == '--'


def _scenario_is_suitable(scenario, comm, name):
    try:
        node = {'type': 'BASH-COMMAND-ENRICHED', 'name': name, 'full name': scenario['name'], 'options': dict(),
                'line': comm['line']}
        cmd = scenario['cmd'].split()
        comm_list = comm['children'].copy()
        comm_list.pop(0)
        accepting_command_options = True

        for i in range(1, len(cmd)):
            if not _scenario_word_is_abstract(cmd[i]):
                if comm_list[0]['type'] != 'BASH-WORD' or comm_list[0]['value'] != cmd[i]:
                    return None
                comm_list.pop(0)
            else:
                while len(comm_list) and accepting_command_options and _bash_word_is_an_option(comm_list[0]):
                    if _bash_word_is_a_skip_word(comm_list[0]):
                        comm_list.pop(0)
                        accepting_command_options = False
                        break
                    _scenario_fit_option(scenario, comm_list, node)
                if _scenario_word_is_a_required_abstraction(cmd[i]):
                    if len(comm_list) == 0:
                        raise exception.EnrichCommandException('Required argument is not provided')
                    node[_scenario_abstract_word_name(cmd[i])] = comm_list.pop(0)
                elif _scenario_word_is_an_optional_abstraction(cmd[i]):
                    if len(comm_list):
                        node[_scenario_abstract_word_name(cmd[i])] = comm_list.pop(0)
                elif _scenario_word_is_an_optional_abstraction_list(cmd[i]):
                    while len(comm_list) > 0:
                        if accepting_command_options and _bash_word_is_an_option(comm_list[0]):
                            _scenario_fit_option(scenario, comm_list, node)
                        else:
                            if node.get(_scenario_abstract_word_name(cmd[i]), None) is None:
                                node[_scenario_abstract_word_name(cmd[i])] = []
                            node[_scenario_abstract_word_name(cmd[i])].append(comm_list.pop(0))

        # to fit options in the end of command
        while len(comm_list) and accepting_command_options and _bash_word_is_an_option(comm_list[0]):
            if _bash_word_is_a_skip_word(comm_list[0]):
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
    if commands_config.get(comm['children'][0]['value'], None) is not None:
        conf = commands_config[comm['children'][0]['value']]['command']
        suitable_scenarios = conf['scenarios'].copy()
        for scenario in suitable_scenarios:
            scenario_res = _scenario_is_suitable(scenario, comm, conf['name'])
            if scenario_res is not None:
                return scenario_res
        globalLog.warning("Suitable scenario not found for command " + comm['line'])
    return comm
