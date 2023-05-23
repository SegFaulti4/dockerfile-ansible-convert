FROM ubuntu-test-stand

RUN apt-get update && \
    apt-get install -qy zsh ksh expect openssl

RUN mkdir /opt/encpass

VOLUME /opt/encpass

