FROM ubuntu-test-stand

RUN apt-get -y update && \
  apt-get -y install \
  curl

CMD bash '/etc/shared/scripts/drive'
