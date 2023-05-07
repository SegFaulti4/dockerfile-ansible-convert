# Perdocker
#
# VERSION               0.0.1

FROM ubuntu-test-stand
MAINTAINER Nox73

RUN groupadd perdocker
RUN useradd -g perdocker perdocker

USER perdocker
