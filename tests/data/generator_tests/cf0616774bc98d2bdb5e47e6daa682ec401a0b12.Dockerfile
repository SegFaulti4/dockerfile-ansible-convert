FROM ubuntu-test-stand

RUN apt-get update && \
    apt-get install -q -y iproute2 curl dnsutils tcpdump iputils-ping net-tools telnet
