FROM ubuntu-test-stand

RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && \
    apt-get install -y --force-yes qemu && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
