FROM ubuntu-test-stand

RUN apt-get update -y && apt-get install -y --no-install-recommends \
  ca-certificates \
  make \
  perl \
  gcc-multilib \
  libc6-dev
