FROM ubuntu-test-stand
MAINTAINER Casey Davenport <casey@tigera.io> 

RUN apt-get update
RUN apt-get install -y iptables

ENTRYPOINT ["/bin/sh"]
