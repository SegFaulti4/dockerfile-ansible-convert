FROM ubuntu-test-stand
  
MAINTAINER Denis Trifonov <destrifonov@gmail.com>  
  
VOLUME /opt/graphite/storage/ceres  
VOLUME /opt/graphite/storage/whisper  
  
CMD ["/bin/sh"]

