FROM ubuntu-test-stand
RUN apt-get update
RUN apt-get install -y \
    linux-tools-common \
    linux-tools-generic \
    linux-tools-`uname -r`

