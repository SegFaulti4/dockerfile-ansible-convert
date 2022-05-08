import tests.instance_utils
import os


os.environ['OS_CLIENT_CONFIG_FILE'] = "../tests/clouds.yaml"
os.chdir('../tests')
tests.instance_utils.setup_instance()
tests.instance_utils.destroy_instance()
