FROM ubuntu-test-stand
MAINTAINER Rohit Menon <rohit.m@en`durance.com>  
RUN apt-get update && apt-get -y install sshguard  
ENTRYPOINT ["/usr/sbin/sshguard"]  

