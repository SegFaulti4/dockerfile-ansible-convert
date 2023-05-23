FROM ubuntu-test-stand
RUN apt-get update && apt-get -y install git
RUN git clone https://github.com/openeyes/oe_installer.git /openeyes

