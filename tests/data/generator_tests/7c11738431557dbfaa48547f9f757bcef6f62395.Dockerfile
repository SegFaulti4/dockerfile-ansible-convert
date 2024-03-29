FROM ubuntu-test-stand

RUN apt-get update -y && apt-get install -y --no-install-recommends \
  ca-certificates \
  make \
  perl \
  gcc \
  libc6-dev \
  gcc-aarch64-linux-gnu \
  libc6-dev-arm64-cross
ENV CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_RUNNER=true \
  CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc
