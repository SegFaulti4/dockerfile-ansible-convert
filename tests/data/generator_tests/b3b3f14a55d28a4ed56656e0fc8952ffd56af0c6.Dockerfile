#Ubuntu based container  
FROM ubuntu-test-stand
  
#MAINTANER  
MAINTAINER dev@adiazmor.com  
  
#RUN Commands  
RUN apt-get update  
RUN apt-get install inetutils-ping -y  

