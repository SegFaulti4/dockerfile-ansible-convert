FROM ubuntu-test-stand
  
RUN apt-get update && \  
apt-get install -y icecc --no-install-recommends && \  
apt-get clean && \  
rm -rf /var/lib/apt/lists/*  

