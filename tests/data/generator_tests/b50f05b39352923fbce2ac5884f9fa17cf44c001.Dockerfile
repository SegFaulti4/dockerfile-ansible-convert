FROM ubuntu-test-stand
RUN apt-get update -y  
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils  
CMD ["echo". "Done"]  

