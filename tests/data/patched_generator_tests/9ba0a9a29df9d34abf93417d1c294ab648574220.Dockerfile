FROM ubuntu-test-stand
MAINTAINER Cseh Ferenc  
  
RUN apt-get update \  
&& apt-get -y upgrade \  
&& apt-get -y install mc  
  
WORKDIR /root  

