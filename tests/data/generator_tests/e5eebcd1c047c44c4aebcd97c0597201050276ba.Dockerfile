FROM ubuntu-test-stand

RUN apt-get update
RUN apt-get install -y openssl

ENV PATH /usr/local/bin/:/usr/bin:/bin
