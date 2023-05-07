FROM ubuntu-test-stand
  
MAINTAINER Dreae <thedreae@gmail.com>  
  
RUN apt-get update && apt-get upgrade -y  
RUN apt-get install -y mingw-w64  

