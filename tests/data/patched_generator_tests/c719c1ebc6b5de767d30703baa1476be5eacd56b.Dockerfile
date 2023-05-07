FROM ubuntu-test-stand
ARG packages="ftp-proxy avahi-daemon"
RUN apt-get update && apt-get install -y $packages && dpkg -l $packages
EXPOSE 2121
