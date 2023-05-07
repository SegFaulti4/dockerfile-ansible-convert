FROM ubuntu-test-stand
MAINTAINER Erik Osterman "e@osterman.com"  
ENV RSYNC_PASSWORD foobar  
  
RUN apt-get update && \  
apt-get -y install rsync  
  
ENTRYPOINT ["/usr/bin/rsync"]  
  

