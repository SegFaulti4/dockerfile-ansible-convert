FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y sl && apt-get clean  
ENTRYPOINT ["/usr/games/sl"]  

