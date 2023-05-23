FROM ubuntu-test-stand
  
RUN apt-get update && apt-get install locales && locale-gen en_US.UTF-8  
ENV LANG=en_US.UTF-8  
ENV LANGUAGE=en_US:en  
ENV LC_ALL=en_US.UTF-8  

