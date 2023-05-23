# Example Dockerfile from
# https://docs.docker.com/userguide/dockerimages/
FROM ubuntu-test-stand
MAINTAINER Doug Richardson <dougie.richardson@gmail.com>
RUN apt-get update && apt-get install -y ruby ruby-dev
RUN gem install sinatra

