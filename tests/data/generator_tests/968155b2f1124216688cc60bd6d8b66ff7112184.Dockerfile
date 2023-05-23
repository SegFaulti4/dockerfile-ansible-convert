# Download base image ubuntu 16.04
FROM ubuntu-test-stand

# Update Ubuntu Software repository
RUN apt-get update \
    && apt-get install -y --force-yes \
        rsyslog \
        sudo \
        openssl \
        acl
