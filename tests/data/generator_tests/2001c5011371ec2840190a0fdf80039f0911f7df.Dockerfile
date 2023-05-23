FROM ubuntu-test-stand
WORKDIR /app
CMD while true ; do nc -l 8080 < /app/index.html ; done
