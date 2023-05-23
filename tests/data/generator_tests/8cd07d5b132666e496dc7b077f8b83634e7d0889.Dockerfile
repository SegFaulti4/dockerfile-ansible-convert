FROM ubuntu-test-stand
MAINTAINER Antal Horvath <antal.horvath@serious-mail.com>  
  
RUN apt-get update \  
&& apt-get -y upgrade \  
&& apt-get -y install mc  
  
WORKDIR /root  

