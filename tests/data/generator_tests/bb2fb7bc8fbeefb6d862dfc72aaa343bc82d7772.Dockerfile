FROM ubuntu-test-stand
MAINTAINER DibbsZA

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get -y -qq upgrade && \
    apt-get -y -qq install software-properties-common && \
    add-apt-repository ppa:ethereum/ethereum && \
    apt-get update && \
    apt-get -y -qq install geth solc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 20000
EXPOSE 20010

ENTRYPOINT ["/usr/bin/geth"]
