import bashlex
import json
import logging
from phase_2 import parse_bashlex
from phase_2.main import phase_2_parse_bash_command
from phase_3 import enrich
from phase_3.main import phase_3_process
from ast2playbook.main import bash_command_to_task
from log import globalLog

globalLog.setLevel(logging.INFO)


with open('./dataset/bash_sandbox.txt', 'r') as inF:
    enrich.init_commands_config()

    for bash_line in inF.readlines():
        print("bashlex:")
        print(bashlex.parse(bash_line)[0].dump())

        parsed = phase_2_parse_bash_command(bash_line)
        print("\nphase_2:")
        print(json.dumps(parsed, indent=4, sort_keys=True))
        if parsed:
            parsed = phase_3_process({'type': 'DOCKERFILE', 'children': [
                {'type': 'DOCKER-ENV', 'name': 'E0'},
                {'type': 'DOCKER-RUN', 'children': parsed}
            ]})
            print("\nphase_3:")
            print(json.dumps(parsed, indent=4, sort_keys=True))

            ast = {'hosts': 'localhost',
                   'name': 'Generated from dockerfile',
                   'tasks': list()}
            bash_command_to_task(ast, parsed)

            print("\nfinal:")
            print(json.dumps(ast, indent=4, sort_keys=True))
