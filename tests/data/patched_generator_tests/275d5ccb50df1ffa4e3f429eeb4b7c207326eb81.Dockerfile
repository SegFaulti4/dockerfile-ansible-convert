FROM ubuntu-test-stand
MAINTAINER docker "jet"  
RUN apt-get update && apt-get install -y nginx  
CMD ["nginx", "-g", "daemon off;"]  

