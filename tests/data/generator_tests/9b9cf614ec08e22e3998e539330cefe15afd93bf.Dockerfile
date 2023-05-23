# Version: 0.0.1  
FROM ubuntu-test-stand
MAINTAINER Florian Schönherr <code@the-anvil.net>  
  
RUN apt-get update && apt-get install -y nginx  
RUN echo 'Hello world' > /usr/share/nginx/html/index.html  
EXPOSE 80  
CMD ["nginx", "-g", "daemon off;"]

