FROM ubuntu-test-stand
  
RUN apt-get update \  
&& apt-get install -y sudo curl \  
&& sudo rm -rf /var/lib/apt/lists/*  

