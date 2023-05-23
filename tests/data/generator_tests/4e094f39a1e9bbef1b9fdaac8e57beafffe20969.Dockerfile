FROM ubuntu-test-stand
MAINTAINER GoCD Team <go-cd@googlegroups.com>

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install fakeroot apt-transport-https curl
