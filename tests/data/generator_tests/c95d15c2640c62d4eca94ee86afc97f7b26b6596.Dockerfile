FROM ubuntu-test-stand
  
RUN apt update  
RUN apt install -y curl  
RUN apt install -y vim  
RUN apt install -y inetutils-ping  

