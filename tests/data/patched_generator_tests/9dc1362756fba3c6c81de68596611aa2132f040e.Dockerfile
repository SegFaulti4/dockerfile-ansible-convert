FROM ubuntu-test-stand
MAINTAINER PentaCode
RUN apt-get install -y  apache2
EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]]
