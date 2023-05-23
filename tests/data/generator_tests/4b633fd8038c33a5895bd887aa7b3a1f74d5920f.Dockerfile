FROM ubuntu-test-stand

RUN apt-get -y update && \
    apt-get -y install ca-certificates
