FROM ubuntu-test-stand
MAINTAINER Docker Education Team <education@docker.com>  
  
RUN apt-get update  
  
ENTRYPOINT [ "/bin/ls" ]  

