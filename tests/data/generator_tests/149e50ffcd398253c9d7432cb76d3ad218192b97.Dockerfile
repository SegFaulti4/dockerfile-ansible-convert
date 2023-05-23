FROM ubuntu-test-stand

MAINTAINER how2dock@gmail.com

RUN apt-get update
RUN apt-get install -y nginx

RUN echo "foobar uses Docker" > /usr/share/nginx/html/index.html

CMD ["nginx","-g","daemon off;"]

EXPOSE 80
