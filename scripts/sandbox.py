import bashlex
import json
import logging
from phase_2 import parse_bashlex
from phase_2.main import phase_2_parse_bash
from phase_3 import enrich
from phase_3.main import phase_3_process
from log import globalLog

globalLog.setLevel(logging.INFO)


with open('./dataset/in.txt', 'r') as inF:
    enrich.init_commands_config()

    for bash_line in inF.readlines():
        parsed = phase_2_parse_bash(bash_line)
        print(parsed)
        if parsed is not None:
            parsed = phase_3_process(parsed)
            print(json.dumps(parsed, indent=4, sort_keys=True))

    '''children = [{'type': 'BASH-COMMAND'}, {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-OR'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'},
                {'type': 'BASH-OPERATOR-AND'}, {'type': 'BASH-COMMAND'}]
    tree = _bashlex_logical_expression_tree(children)
    print(tree)'''
