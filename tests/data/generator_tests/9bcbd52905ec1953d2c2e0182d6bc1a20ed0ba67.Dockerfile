FROM ubuntu-test-stand
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
      kmod \
      libcharon-extra-plugins \
      strongswan \
      iptables \
      curl \
      iputils-ping \
 && rm -rf /var/lib/apt/lists/*
