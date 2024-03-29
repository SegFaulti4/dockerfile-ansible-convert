# A basic apache server. To use either add or bind mount content under /var/www
FROM ubuntu-test-stand

MAINTAINER Kimbro Staken version: 0.1

RUN apt-get update && apt-get install -y apache2 && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV APACHE_RUN_USER=www-data APACHE_LOG_DIR=/var/log/apache2
ENV APACHE_RUN_GROUP=www-data

EXPOSE 80

CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]
