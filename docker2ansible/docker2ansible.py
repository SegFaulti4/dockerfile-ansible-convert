import logging
import argparse
import sys

import docker2ansible.phase_1.phase_1
import docker2ansible.phase_2.phase_2
import docker2ansible.phase_3.phase_3
import docker2ansible.phase_3.enrich
import docker2ansible.ast2playbook.ast2playbook
from docker2ansible.log import globalLog

globalLog.setLevel(logging.DEBUG)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('dockerfile', action='store', help='Path to dockerfile')
    parser.add_argument('-o', '--output', action='store',
                        help='Path to resulting file, if not provided stdout will be used')
    return parser.parse_args()


def main(dockerfile_path, out_stream=sys.stdout):
    obj = docker2ansible.phase_1.phase_1.phase_1_obj_from_path(dockerfile_path)
    obj = docker2ansible.phase_2.phase_2.phase_2_process(obj)
    obj = docker2ansible.phase_3.phase_3.phase_3_process(obj)
    obj = docker2ansible.ast2playbook.ast2playbook.ast2playbook_process(obj)
    docker2ansible.ast2playbook.ast2playbook.dump_playbook(obj, out_stream)


if __name__ == '__main__':
    args = parse_arguments()
    dp = args.dockerfile
    out_s = open(args.output, 'w') if args.output else sys.stdout
    main(dockerfile_path=dp, out_stream=out_s)
