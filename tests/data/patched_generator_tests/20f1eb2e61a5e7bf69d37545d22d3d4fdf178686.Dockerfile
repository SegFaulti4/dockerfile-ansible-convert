FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y ssh iproute2 iputils-ping wget
