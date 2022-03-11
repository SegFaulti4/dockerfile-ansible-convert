import json
import sys

from exception import ConvertException
from log import globalLog


def _mine_sh(json_o):
    if json_o.get('type', '') == 'MAYBE-BASH':
        return [json_o['line']]

    res = []
    if 'children' in json_o.keys():
        for child in json_o['children']:
            res.extend(_mine_sh(child))

    return res


def _bash_line_preproc(line):
    return ' '.join(map(lambda x: x.strip(), line.replace('\n', ' ').replace('\t', ' ').split(' ')))


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as in_f:
        ph_1 = json.load(in_f)

        bash_lines = []
        for json_o in ph_1:
            bash_lines.extend(_mine_sh(json_o))

        with open(sys.argv[1] + '.mined', 'w') as out_mine:
            for line in bash_lines:
                out_mine.write(_bash_line_preproc(line) + '\n')
