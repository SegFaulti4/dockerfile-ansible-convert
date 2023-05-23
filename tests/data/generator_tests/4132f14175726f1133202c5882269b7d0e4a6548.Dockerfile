FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y \
  autoconf \
  bison \
  flex \
  g++ \
  make
WORKDIR /usr/src/app
