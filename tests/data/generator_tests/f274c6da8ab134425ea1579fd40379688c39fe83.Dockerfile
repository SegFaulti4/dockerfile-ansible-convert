from ubuntu-test-stand
MAINTAINER Austin G. Davis-Richardson <harekrishna@gmail.com>  
  
LABEL description="Run password-store and GnuPG inside of a Docker container"  
  
RUN apt-get update  
  
RUN apt-get install -y pass pinentry-curses  

