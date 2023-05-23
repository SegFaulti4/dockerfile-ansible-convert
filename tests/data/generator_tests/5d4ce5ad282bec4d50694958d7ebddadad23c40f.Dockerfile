FROM ubuntu-test-stand
  
RUN apt-get update && \  
apt-get install -y --no-install-recommends rmlint bash  
  
CMD ["/bin/bash"]  

