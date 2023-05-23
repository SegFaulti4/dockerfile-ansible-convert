FROM ubuntu-test-stand
MAINTAINER Aqsa  
RUN apt-get update  
RUN apt-get install nano  
CMD ["php", "-a"]  

