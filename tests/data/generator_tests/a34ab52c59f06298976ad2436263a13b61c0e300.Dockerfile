FROM ubuntu-test-stand

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

RUN apt-get update && \
    apt-get install -y \
      curl \
      g++ \
      git \
      make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
