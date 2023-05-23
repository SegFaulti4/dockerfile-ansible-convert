FROM ubuntu-test-stand
RUN apt-get -yq update
RUN apt-get install -yq dnsutils curl netcat
