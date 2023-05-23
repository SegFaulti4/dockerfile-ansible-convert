FROM ubuntu-test-stand

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

RUN apt-get update && \
    apt-get install -y \
      gcc \
      make \
      wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

