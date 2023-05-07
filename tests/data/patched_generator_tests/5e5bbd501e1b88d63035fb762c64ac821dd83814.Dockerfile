FROM ubuntu-test-stand

MAINTAINER Rob Syme <rob.syme@gmail.com>

RUN apt-get update -qq && apt-get install -qqy bedtools samtools
