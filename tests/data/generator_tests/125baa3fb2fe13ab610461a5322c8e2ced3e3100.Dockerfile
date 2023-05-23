FROM ubuntu-test-stand

RUN apt-get update && apt-get -y install \
    suckless-tools

ENV IN_DOCKER_CONTAINER True
