# Basic image to compile
FROM ubuntu-test-stand
MAINTAINER Sten Feldman <exile@chamber.ee>
RUN apt-get update
RUN apt-get install -y lib32stdc++6 make
CMD "/usr/bin/make"
