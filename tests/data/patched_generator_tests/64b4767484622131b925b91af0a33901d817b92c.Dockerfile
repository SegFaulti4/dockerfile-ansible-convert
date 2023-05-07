FROM ubuntu-test-stand

RUN apt-get update -yq && apt-get install -yq netcat
