FROM ubuntu-test-stand
LABEL maintainer "Benjamin Stein <info@diffus.org>"  
RUN apt-get update \  
&& apt-get -y install ansible \  
&& apt-get clean \  
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*  
CMD ["/bin/bash"]  

