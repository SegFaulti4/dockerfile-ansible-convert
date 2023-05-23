FROM ubuntu-test-stand
RUN apt-get update ; apt-get dist-upgrade -y -qq 
RUN apt-get install -y -qq wget

