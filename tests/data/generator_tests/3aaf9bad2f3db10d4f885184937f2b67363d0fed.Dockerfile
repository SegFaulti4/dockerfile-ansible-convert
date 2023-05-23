# taken from https://docs.docker.com/engine/userguide/containers/dockerimages/ 
FROM ubuntu-test-stand
MAINTAINER Kate Smith <ksmith@example.com>
RUN apt-get update && apt-get install -y ruby ruby-dev
RUN gem install sinatra
