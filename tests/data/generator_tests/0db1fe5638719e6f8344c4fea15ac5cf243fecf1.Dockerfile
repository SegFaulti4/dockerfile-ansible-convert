FROM ubuntu-test-stand
MAINTAINER Trifacta, Inc.

RUN apt-get update && apt-get install -y dnsmasq

USER root
CMD ["dnsmasq", "--no-daemon"]
