# Simple Dockerfile for testing docker cloud repository  
FROM ubuntu-test-stand
MAINTAINER centrifugal4@gmail.com  
  
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential python3-dev python3-pip python3-setuptools  

