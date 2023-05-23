FROM ubuntu-test-stand
RUN apt update && apt install -y nginx  
CMD nginx -g 'daemon off;'  
  

