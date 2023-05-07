#  
# Ubuntu Dockerfile  
#  
# https://github.com/buddho-io/docker-ubuntu  
#  
# Pull base image.  
FROM ubuntu-test-stand
# Intall.  
RUN \  
apt-get update && \  
apt-get upgrade -y && \  
rm -rf /var/lib/apt/lists/*  
  
# Set environment variables.  
ENV HOME /root  
  
# Define working directory.  
WORKDIR /root  
  
# Define default command.  
CMD ["bash"]  

