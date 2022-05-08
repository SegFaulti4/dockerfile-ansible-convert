import json
import yaml
import logging

from dockerfile_ansible_convert.dockerfile_ast import create_from_path
from dockerfile_ansible_convert.generator import PlaybookGenerator
from log import globalLog


globalLog.setLevel(logging.INFO)
dockerfile_path = './data/dockerfile_sandbox'
playbook_path = './data/dockerfile_sandbox.yml'

ast = create_from_path(dockerfile_path)
generator = PlaybookGenerator(ast=ast)
playbook = generator.generate()

print(json.dumps(playbook, indent=4, sort_keys=True))
yaml.dump(playbook, open(playbook_path, "w"))
