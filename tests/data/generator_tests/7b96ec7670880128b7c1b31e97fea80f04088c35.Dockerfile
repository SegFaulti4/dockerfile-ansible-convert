FROM ubuntu-test-stand

ENV DEBIAN_FRONTEND noninteractive

RUN \
  apt-get update && \
  apt-get upgrade -y && \
  apt-get clean

RUN \
  apt-get -y install ghostscript && \
  apt-get clean

ENTRYPOINT ["gs"]
