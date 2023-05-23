FROM ubuntu-test-stand
  
RUN apt update && apt install -y curl git zip  
  
CMD ["bash"]  

