FROM ubuntu-test-stand
ARG packages="squid avahi-daemon"
RUN apt-get update && apt-get install -y $packages && dpkg -l $packages
EXPOSE 3128-3130
