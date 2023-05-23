FROM ubuntu-test-stand

RUN apt-get install -y python2.7

CMD ["/sbin/init"]
