# Version: 0.0.1  
FROM ubuntu-test-stand
MAINTAINER Drew Bisset "drew@wellmatchhealth.com"  
RUN apt-get update  
RUN apt-get install -y nginx  
RUN echo "Engine-x'ing yo' self, seen!" > /usr/share/nginx/html/index.html  
EXPOSE 80  

