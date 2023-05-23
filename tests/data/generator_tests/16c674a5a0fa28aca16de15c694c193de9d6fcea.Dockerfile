FROM ubuntu-test-stand
  
RUN apt-get update  
RUN apt-get install -y procps  
RUN apt-get install -y aptitude  
RUN apt-get install -y vim  
RUN apt-get install -y unzip  
  

