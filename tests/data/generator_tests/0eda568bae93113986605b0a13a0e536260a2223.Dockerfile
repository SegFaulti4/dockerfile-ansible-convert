FROM ubuntu-test-stand
RUN apt-get install -y nfs-kernel-server
VOLUME ["/export"]
