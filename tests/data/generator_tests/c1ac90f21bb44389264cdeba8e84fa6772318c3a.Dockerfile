FROM ubuntu-test-stand

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
	make \
	sudo
