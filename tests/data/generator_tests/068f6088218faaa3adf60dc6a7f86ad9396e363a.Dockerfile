# This docker file builds an image that runs curl
FROM ubuntu-test-stand
RUN apt-get -y update && apt-get install -y curl
