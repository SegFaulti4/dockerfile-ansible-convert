FROM ubuntu-test-stand
  
RUN \  
apt-get update \  
&& apt-get -yyq --force-yes install curl wget \  
&& rm -rf /var/lib/apt/*  

