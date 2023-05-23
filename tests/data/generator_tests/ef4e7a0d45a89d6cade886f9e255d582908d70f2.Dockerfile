########################################  
# DockerFile to build new image  
########################################  
FROM ubuntu-test-stand
MAINTAINER shankar <bunny.shankar@gmail.com>  
RUN mkdir mynewdir  
RUN echo 'this is my new container' > /mynewdir/mynewfile  
RUN mkdir automatedBuilds  

