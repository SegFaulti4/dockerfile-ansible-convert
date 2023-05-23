FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  libc6-dev \
  ca-certificates \
  musl-tools
