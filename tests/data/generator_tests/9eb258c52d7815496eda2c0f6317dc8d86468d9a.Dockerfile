FROM ubuntu-test-stand
  
RUN apt update -y &&\  
apt upgrade -y &&\  
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*  

