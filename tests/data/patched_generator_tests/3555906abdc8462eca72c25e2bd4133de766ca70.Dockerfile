FROM ubuntu-test-stand

MAINTAINER Douglas Holt <dholt@nvidia.com>

RUN apt-get update && \
    apt-get -y install dnsmasq

VOLUME /etc/dnsmasq.d

#ENTRYPOINT ["dnsmasq"]
CMD ["dnsmasq", "-d"]
