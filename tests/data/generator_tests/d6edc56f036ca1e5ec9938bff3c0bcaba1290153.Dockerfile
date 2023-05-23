FROM ubuntu-test-stand
RUN apt-get install -y nginx
EXPOSE 80
CMD /usr/sbin/nginx -g 'daemon off;'
