FROM ubuntu-test-stand
MAINTAINER Takuya Arita <takuya.arita@gmail.com>  
  
# Install Dependencies  
RUN apt-get update && apt-get install -y bonnie++  
  
# Run bonnie++  
ENTRYPOINT ["bonnie++"]  

