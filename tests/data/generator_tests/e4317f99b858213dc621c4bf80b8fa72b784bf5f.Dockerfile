FROM ubuntu-test-stand
  
ENV DEBIAN_FRONTEND noninteractive  
  
RUN apt-get update  
RUN apt-get install -y \  
curl dnsutils wget  
  

