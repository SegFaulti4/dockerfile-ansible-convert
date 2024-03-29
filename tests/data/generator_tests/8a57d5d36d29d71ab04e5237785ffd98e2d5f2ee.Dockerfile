FROM ubuntu-test-stand
RUN apt-get update
RUN apt-get install -y sudo openssh-server curl lsb-release
RUN apt-get install -y net-tools tar
RUN export LC_ALL=C
RUN curl -sSL https://www.opscode.com/chef/install.sh | sudo bash -s -- -v 12.19.36
