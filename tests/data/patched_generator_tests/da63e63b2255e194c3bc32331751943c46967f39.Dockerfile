FROM ubuntu-test-stand

RUN apt-get update && \
	apt-get install -y reprepro && \
	apt-get clean

VOLUME torus
