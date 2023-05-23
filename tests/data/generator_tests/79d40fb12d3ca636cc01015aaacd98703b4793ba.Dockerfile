FROM ubuntu-test-stand

MAINTAINER Rob Syme <rob.syme@gmail.com>

RUN apt-get update && apt-get install -qqy ncbi-blast+
