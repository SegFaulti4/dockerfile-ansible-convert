FROM ubuntu-test-stand

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

RUN apt-get update && \
    apt-get install -y \
      gcc \
      git \
      m4 \
      make \
      unzip \
      wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

