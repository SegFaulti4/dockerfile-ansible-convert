FROM ubuntu-test-stand

RUN apt-get update && apt-get -y install \
    pdftk

ENV IN_DOCKER_CONTAINER True
