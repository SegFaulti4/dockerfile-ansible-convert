FROM ubuntu-test-stand
MAINTAINER Darksheer  
  
RUN apt-get update -y \  
&& apt-get upgrade -y \  
&& apt-get clean -y \  
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*  

