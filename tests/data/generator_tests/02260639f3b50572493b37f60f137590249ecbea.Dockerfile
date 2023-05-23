FROM ubuntu-test-stand
MAINTAINER Jeff Dickey jeff@dickeyxxx.com  
  
ENV HOME /root  
  
RUN apt-get update  
RUN apt-get install -y vim curl sudo  
RUN apt-get clean  

