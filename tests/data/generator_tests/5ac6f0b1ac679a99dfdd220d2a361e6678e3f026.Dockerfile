
FROM ubuntu-test-stand

RUN apt-get update

CMD while true; do echo hello world; sleep 1; done
