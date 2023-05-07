FROM ubuntu-test-stand
LABEL maintainer="james@example.com"
ENV REFRESHED_AT 2016-06-01
RUN apt-get -qq update
