FROM ubuntu-test-stand
RUN apt-get update  
RUN apt-get install -y nginx  
RUN echo 'Hello World!!!' >/usr/share/nginx/html/index.html  
EXPOSE 80  

