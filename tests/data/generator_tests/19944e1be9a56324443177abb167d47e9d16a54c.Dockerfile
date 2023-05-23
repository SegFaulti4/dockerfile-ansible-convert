FROM ubuntu-test-stand

RUN apt-get update
RUN apt-get -y install iputils-ping netcat curl iproute2 

