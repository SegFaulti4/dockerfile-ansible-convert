import argparse
import sys
import yaml

import dockerfile_ansible_convert.generator as generator
from log import globalLog


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('dockerfile', action='store', help='Path to dockerfile')
    parser.add_argument('-o', '--output', action='store',
                        help='Path to resulting file, if not provided stdout will be used')
    return parser.parse_args()


def create_playbook_from_dockerfile(dockerfile_path, out_stream=sys.stdout):
    playbook = generator.generate_from_dockerfile(dockerfile_path)
    try:
        yaml.dump(playbook, out_stream)
    except Exception as exc:
        globalLog.error(exc)


def main():
    args = parse_arguments()
    dp = args.dockerfile
    out_s = open(args.output, 'w') if args.output else sys.stdout
    create_playbook_from_dockerfile(dockerfile_path=dp, out_stream=out_s)
