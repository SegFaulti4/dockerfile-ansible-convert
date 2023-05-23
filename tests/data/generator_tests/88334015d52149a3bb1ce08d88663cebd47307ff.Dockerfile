FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y nkf && apt-get clean  
ENTRYPOINT ["nkf"]  

