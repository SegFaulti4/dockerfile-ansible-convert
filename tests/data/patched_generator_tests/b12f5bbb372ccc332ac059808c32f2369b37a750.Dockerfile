FROM ubuntu-test-stand
MAINTAINER Zach Latta <zach@hackclub.com>

RUN apt-get update
RUN apt-get install -y ledger

ENTRYPOINT /bin/bash
