from ubuntu-test-stand

run apt-get update && apt-get install -y beanstalkd
volume ["/beanstore"]
cmd ["beanstalkd", "-b", "/beanstore"]