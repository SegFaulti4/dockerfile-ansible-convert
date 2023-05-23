FROM ubuntu-test-stand
RUN apt-get update && apt-get upgrade -y && apt-get clean  
  
#nfs client install  
RUN apt-get install -y nfs-common  
  
VOLUME /mnt  
  
#mount  
CMD /etc/init.d/rpcbind start && mount nfshost:/nfs /mnt  

