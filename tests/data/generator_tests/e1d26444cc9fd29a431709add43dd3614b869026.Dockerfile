FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y --no-install-recommends redis-server iperf3 dnsutils
