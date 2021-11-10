import argparse
import json
import sys

import bashlex
from bashlex import errors

from exception import ConvertException
from log import globalLog


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, required=False)
    arguments = parser.parse_args()
    return arguments


def process(obj):
    return json.dumps(obj, indent=4, sort_keys=True)


def _write_processed_phase_2(out_file, obj, prefix=None):
    if prefix is None:
        prefix = ''

    globalLog.info('Phase 2 of dockerfile from ' + obj['source_name'])
    try:
        out_file.write(prefix + process(obj))
    except Exception as ex:
        globalLog.warning(ex)
        pass


if __name__ == '__main__':
    args = parse_arguments()

    out_file = sys.stdout
    if args.file:
        try:
            out_file = open(args.file, 'w', newline='')
        except OSError as os_ex:
            globalLog.warning(os_ex)
            globalLog.info("Redirect file output into stdout")

    ph_1 = json.load(sys.stdin)
    out_file.write('[')
    _write_processed_phase_2(out_file, ph_1[0], prefix='')
    for obj in ph_1[1:]:
        _write_processed_phase_2(out_file, ph_1[0], prefix=',\n')
    out_file.write(']\n')
