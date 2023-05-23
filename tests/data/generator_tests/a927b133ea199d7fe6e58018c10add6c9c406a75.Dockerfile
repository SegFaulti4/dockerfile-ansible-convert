FROM ubuntu-test-stand
RUN apt-get update -qq ; apt-get dist-upgrade -y -qq
RUN apt-get install -y -qq redis-server
CMD redis-server
EXPOSE 6379