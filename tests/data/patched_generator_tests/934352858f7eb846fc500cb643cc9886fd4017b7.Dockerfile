FROM ubuntu-test-stand

run apt-get update      \
  && apt-get -y install \
    curl         \
    iproute2     \
    iputils-ping \
    netcat
