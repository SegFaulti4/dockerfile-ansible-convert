FROM ubuntu-test-stand
MAINTAINER Jeff Nickoloff <jeff@allingeek.com>  
RUN apt-get update && apt-get install -y htop  
CMD htop  

