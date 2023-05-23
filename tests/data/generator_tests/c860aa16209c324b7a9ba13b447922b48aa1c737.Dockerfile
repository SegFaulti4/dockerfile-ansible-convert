# test  
FROM ubuntu-test-stand
  
  
RUN apt-get update && apt-get install curl \  
htop -y  

