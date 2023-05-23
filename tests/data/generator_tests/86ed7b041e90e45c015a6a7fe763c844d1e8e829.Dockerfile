FROM ubuntu-test-stand
MAINTAINER Daisuke Baba  
  
RUN ( \  
apt-get -qq update && \  
apt-get -qq install make git gcc-arm-none-eabi gyp ninja-build \  
)  
  
CMD bash  

