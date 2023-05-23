############################  
# Dockerfile to build an Apache2 image  
############################  
# Base image is Ubuntu  
FROM ubuntu-test-stand
  
# Author: Dung Ho  
MAINTAINER Dung-Ho <dung.hoduy@asnet.com.vn>  
  
# Create 'mydir' and 'myfile'  
RUN mkdir mydir  
RUN touch mydir/myfile  
RUN echo 'this is my testing for container' > mydir/myfile  
RUN echo 'this is content for trigger bulding' > mydir/myfile

