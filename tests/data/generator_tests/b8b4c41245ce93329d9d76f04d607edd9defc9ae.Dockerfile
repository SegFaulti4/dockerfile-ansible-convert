#Generate a Docker image
FROM ubuntu-test-stand
MAINTAINER Moycat
RUN apt-get update
RUN apt-get -y install g++ fp-compiler
