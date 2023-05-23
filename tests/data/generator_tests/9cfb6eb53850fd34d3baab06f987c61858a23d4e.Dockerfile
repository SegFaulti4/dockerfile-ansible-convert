FROM ubuntu-test-stand
MAINTAINER Sergey Matyukevich <s-matyukevich@gmail.com>
RUN apt-get update && apt-get install -y curl iputils-ping iproute2 net-tools tcpdump vim 
