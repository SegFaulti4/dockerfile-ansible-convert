FROM ubuntu-test-stand
  
RUN apt-get update \  
&& apt-get install -y gnustep-base-runtime \  
&& rm -rf /var/lib/apt/lists/*  

