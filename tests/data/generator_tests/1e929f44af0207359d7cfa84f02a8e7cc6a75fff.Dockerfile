FROM ubuntu-test-stand
ADD https://get.docker.com/builds/Linux/x86_64/docker-1.8.0 /usr/bin/docker  
RUN chmod +x /usr/bin/docker  

