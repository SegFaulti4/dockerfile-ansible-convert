FROM ubuntu-test-stand
WORKDIR /app  
RUN apt-get update \  
&& apt-get install -y inetutils-ping dnsutils wget curl vim git  

