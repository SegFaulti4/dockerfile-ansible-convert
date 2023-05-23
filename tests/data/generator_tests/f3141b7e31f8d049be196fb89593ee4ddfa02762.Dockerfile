# vim: syntax=dockerfile

FROM ubuntu-test-stand

# Install ifconfig and iperf3
RUN apt-get -q update
RUN apt-get install -y net-tools iperf3 iputils-ping ethtool tcpdump tmux iproute2
RUN apt-get -q update

