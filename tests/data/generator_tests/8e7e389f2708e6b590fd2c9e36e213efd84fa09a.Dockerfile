FROM ubuntu-test-stand
MAINTAINER Feng Honglin <hfeng@tutum.co>

RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists
