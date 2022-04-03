import logging
import argparse
import sys

import phase_1.main
import phase_2.main
import phase_3.main
import phase_3.enrich
import ast2playbook.main
import exception
from log import globalLog

globalLog.setLevel(logging.DEBUG)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', action='store', dest='in_file', help='Path to dockerfile')
    parser.add_argument('-o', '--output', action='store', dest='out_file', help='Path to resulting file')
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    dockerfile_path = args.in_file if args.in_file else './Dockerfile'
    out_stream = open(args.out_file, 'w') if args.out_file else sys.stdout

    obj = phase_1.main.phase_1_obj_from_path(dockerfile_path)
    obj = phase_2.main.phase_2_process(obj)
    phase_3.enrich.init_commands_config()
    obj = phase_3.main.phase_3_process(obj)
    obj = ast2playbook.main.ast2playbook_process(obj)
    ast2playbook.main.dump_playbook(obj, out_stream)


if __name__ == '__main__':
    main()
