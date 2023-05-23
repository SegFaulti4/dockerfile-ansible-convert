# This is a comment
FROM ubuntu-test-stand
MAINTAINER Alex Korovyansky <korovyansk@gmail.com>

EXPOSE 8081

RUN apt-get -qq update
RUN apt-get -qqy install mc lighttpd