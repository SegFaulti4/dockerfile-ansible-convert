import bashlex
import json
import logging
from docker2ansible.phase_2.phase_2 import phase_2_parse_bash_command
from docker2ansible.phase_3.phase_3 import phase_3_process
from docker2ansible.log import globalLog

globalLog.setLevel(logging.INFO)


def main():
    with open('./bash_sandbox', 'r') as inF:

        for bash_line in inF.readlines():
            print("bashlex:")
            print(bashlex.parse(bash_line)[0].dump())

            if True:
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


if __name__ == '__main__':
    main()
