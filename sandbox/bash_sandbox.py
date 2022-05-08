import bashlex
import json
import logging

from dockerfile_ansible_convert.bash_parse import parse_bash_commands
from log import globalLog


globalLog.setLevel(logging.INFO)
with open('./data/bash_sandbox', 'r') as inF:

    for bash_line in inF.readlines():
        print("bashlex:")
        for part in bashlex.parse(bash_line):
            print(part.dump())

        parsed = parse_bash_commands(bash_line)
        print("\nbash_parse:")
        print(json.dumps(parsed, indent=4, sort_keys=True, default=lambda o: o.__dict__))
