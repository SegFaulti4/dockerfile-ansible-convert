from ubuntu-test-stand

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y curl

ENTRYPOINT ["curl", "--retry", "5", "-X", "PUT", "-T"]

