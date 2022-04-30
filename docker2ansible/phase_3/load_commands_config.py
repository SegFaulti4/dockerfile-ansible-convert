"""
def init_commands_config():
    path = './docker2ansible/config/'
    for filename in glob.glob(os.path.join(path, '*.yml')):
        with open(os.path.join(os.getcwd(), filename), 'r') as _f:  # open in readonly mode
            try:
                commands_config[filename[len(path):filename.find('.yml')]] = yaml.safe_load(_f)
            except yaml.YAMLError as exc:
                continue
"""
