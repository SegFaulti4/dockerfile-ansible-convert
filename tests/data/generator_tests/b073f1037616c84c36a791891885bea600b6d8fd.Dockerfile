FROM ubuntu-test-stand

MAINTAINER palletOne "contract@pallet.one"

RUN apt-get -y update \
    && apt-get install -yqq wget \
       git \
       gcc 
