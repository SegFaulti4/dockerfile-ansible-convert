FROM ubuntu-test-stand
RUN apt-get update && apt-get install -y curl libcap2-bin grep iproute2 httpie iputils-ping stress schedtool
