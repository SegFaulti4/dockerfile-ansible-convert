FROM ubuntu-test-stand
MAINTAINER napoleonwilson <danieljwilcox@gmail.com>

RUN mkdir -p /home/docker

VOLUME /home/docker
CMD ["true"]