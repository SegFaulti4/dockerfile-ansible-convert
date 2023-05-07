FROM ubuntu-test-stand
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  gcc-multilib libc6-dev ca-certificates
ENV PATH=$PATH:/rust/bin
