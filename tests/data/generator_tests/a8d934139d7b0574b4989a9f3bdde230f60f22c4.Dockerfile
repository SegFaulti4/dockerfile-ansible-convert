FROM ubuntu-test-stand
RUN apt-get update  
RUN apt-get install stress  
CMD /usr/bin/stress --cpu 1  

