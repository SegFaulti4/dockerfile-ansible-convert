FROM ubuntu-test-stand
RUN apt-get update
RUN apt-get install -y debootstrap
RUN apt-get install -dy zfsutils-linux python3-minimal
