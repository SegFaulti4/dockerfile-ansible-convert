FROM ubuntu-test-stand
MAINTAINER Antoni Felix <antoni.felix96@gmail.com>  
  
RUN apt-get -y update \  
&& apt-get -y dist-upgrade \  
&& apt-get -y install mc \  
&& apt-get clean  
  
WORKDIR /root  

