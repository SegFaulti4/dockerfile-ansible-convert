FROM ubuntu-test-stand
MAINTAINER duruo850  
  
# Install packages  
RUN apt-get update && apt-get -y upgrade  
# RUN tools = 'vim g++'  
RUN tools='vim'\  
&&apt-get install -y $tools --no-install-recommends

