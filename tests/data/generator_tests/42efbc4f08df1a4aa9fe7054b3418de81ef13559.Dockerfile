FROM ubuntu-test-stand
MAINTAINER manuel.peuster@uni-paderborn.de

RUN apt-get update && apt-get install -y \
    net-tools \
    iputils-ping \
    iproute2

CMD /bin/bash
