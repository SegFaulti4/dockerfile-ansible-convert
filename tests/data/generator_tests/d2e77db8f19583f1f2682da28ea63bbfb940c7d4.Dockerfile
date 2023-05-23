from ubuntu-test-stand

run apt-get update && \
    apt-get install -y curl

cmd ["curl"]
