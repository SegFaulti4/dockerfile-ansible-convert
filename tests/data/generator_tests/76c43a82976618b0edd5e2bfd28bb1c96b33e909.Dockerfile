FROM ubuntu-test-stand
RUN apt-get update  
RUN apt-get install -y wget  
RUN apt-get install -y vim  
  
CMD ["ping", "127.0.0.1", "-c", "30"]  

