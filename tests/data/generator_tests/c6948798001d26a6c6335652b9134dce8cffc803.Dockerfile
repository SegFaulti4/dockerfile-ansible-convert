FROM ubuntu-test-stand

RUN apt-get update -y && apt-get install -y nasm \
    binutils