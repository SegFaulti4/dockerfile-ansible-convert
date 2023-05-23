FROM ubuntu-test-stand
  
RUN apt-get update \  
&& apt-get upgrade -y \  
&& apt-get install mc -y  
  
  
WORKDIR /root  

