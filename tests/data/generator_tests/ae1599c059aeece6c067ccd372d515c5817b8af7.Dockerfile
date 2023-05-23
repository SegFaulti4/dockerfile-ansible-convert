FROM ubuntu-test-stand

RUN apt-get update -y && apt-get install -y --no-install-recommends \
  gcc \
  libc6-dev \
  ca-certificates

