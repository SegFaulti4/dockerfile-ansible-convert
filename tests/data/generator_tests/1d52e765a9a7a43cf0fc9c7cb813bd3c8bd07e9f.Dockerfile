FROM ubuntu-test-stand
MAINTAINER juergen.rose@ibh-systems.com 

RUN apt-get update
RUN apt-get install -y openjdk-8-jdk-headless screen gdebi-core python2.7 perl rsync sudo

CMD java -version 