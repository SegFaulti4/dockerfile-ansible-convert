FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y \  
vim curl nano iputils-ping  
CMD ["ping", "127.0.0.1", "-c", "20"]  

