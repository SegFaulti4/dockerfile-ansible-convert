FROM ubuntu-test-stand
MAINTAINER Elton Stoneman <elton@sixeyed.com>

RUN mkdir /v1 && touch /v1/file1.es.txt

VOLUME /v1