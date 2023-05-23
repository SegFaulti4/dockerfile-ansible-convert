FROM ubuntu-test-stand

RUN apt-get update && apt-get install -y stress

CMD stress -c 2
