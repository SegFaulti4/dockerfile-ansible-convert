# Dockerfile
FROM ubuntu-test-stand
RUN apt-get update -y
RUN apt-get install figlet -y
CMD figlet -f script hello

