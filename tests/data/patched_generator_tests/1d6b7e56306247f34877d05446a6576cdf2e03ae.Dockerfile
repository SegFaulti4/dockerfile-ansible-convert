FROM ubuntu-test-stand
MAINTAINER Paris Kasidiaris <pariskasidiaris@gmail.com>

RUN mkdir -p /var/opendevelop/bucket
VOLUME ["/var/opendevelop/bucket"]
WORKDIR /var/opendevelop/bucket
