FROM ubuntu-test-stand

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  gcc xz-utils ca-certificates make libc6-dev gdb curl \
  gettext
