FROM ubuntu-test-stand
  
RUN apt-get update && apt-get install -y \  
vim \  
curl \  
wget \  
git \  
net-tools \  
iputils-ping \  
traceroute \  
dnsutils \  
netcat \  
mtr-tiny \  
jq \  
nmap \  
ssh \  
tcpdump \  
netcat \  
tcpflow  
  

