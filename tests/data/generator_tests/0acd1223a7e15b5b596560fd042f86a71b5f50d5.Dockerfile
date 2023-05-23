FROM ubuntu-test-stand

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  gcc ca-certificates make libc6-dev \
  libssl-dev \
  pkg-config
