FROM ubuntu-test-stand

RUN apt-get update && apt-get install -y curl

ENTRYPOINT ["curl", "example.com"]