FROM ubuntu-test-stand
MAINTAINER info@yuki-matsumoto.com

RUN mkdir -p /var/run/sshd
RUN apt-get install -y openssh-server
RUN /bin/sh -c 'echo root:root | chpasswd'
