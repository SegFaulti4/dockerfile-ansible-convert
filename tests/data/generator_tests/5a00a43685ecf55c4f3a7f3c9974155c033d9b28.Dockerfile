FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y \  
libc++1 \  
libc++abi1 \  
vim \  
tmux \  
ssh \  
rsync \  
curl \  
iproute2 \  
iputils-ping  
  
CMD service ssh start && /bin/bash  

