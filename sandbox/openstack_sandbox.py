import tests.instance_utils
import os


def main():
    os.environ['OS_CLIENT_CONFIG_FILE'] = "../tests/clouds.yaml"
    os.chdir('../tests')
    tests.instance_utils.setup_instance()
    tests.instance_utils.destroy_instance()


if __name__ == '__main__':
    main()
