FROM ubuntu-test-stand

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

RUN apt-get update && \
    apt-get install -y \
      build-essential \
      git \
      libssl-dev \
      ncurses-dev \
      wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

