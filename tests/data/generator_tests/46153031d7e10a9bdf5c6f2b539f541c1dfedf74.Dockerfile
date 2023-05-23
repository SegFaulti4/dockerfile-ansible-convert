FROM ubuntu-test-stand

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc-multilib xz-utils ca-certificates make libc6-dev
