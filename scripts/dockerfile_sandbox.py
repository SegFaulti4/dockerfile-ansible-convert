import glob
import os
import json
import logging

import phase_1.main
import phase_2.main
import phase_3.main

import exception
from log import globalLog

globalLog.setLevel(logging.INFO)


def fancy_print(ast):
    print(json.dumps(ast, indent=4, sort_keys=True))


def main():
    path = './dataset/dockerfile_sandbox'
    phase_3.enrich.init_commands_config()
    for filepath in glob.glob(os.path.join(path, 'Dockerfile')):
        # dockerfile parsing
        ast = phase_1.main.parse_dockerfile_from_path(filepath)
        ast = phase_1.main.phase_1_process(parsed_dockerfile=ast, meta_info=path)
        ast = phase_2.main.phase_2_process(obj=ast)
        # ast = phase_3.main.phase_3_process(obj=ast)
        fancy_print(ast)


if __name__ == '__main__':
    main()
