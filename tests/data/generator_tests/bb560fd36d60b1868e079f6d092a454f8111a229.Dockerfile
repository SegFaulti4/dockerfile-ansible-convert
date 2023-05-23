FROM ubuntu-test-stand
MAINTAINER Nick Portokallidis <portokallidis@gmail.com>  
  
RUN apt-get update && apt-get install -y wget git apache2  
  
EXPOSE 80

