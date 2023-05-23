# houston/test/fixture/worker/docker/image1/Dockerfile
# A basic Dockerfile for use in testing the docker class

FROM ubuntu-test-stand

RUN mkdir -p /tmp/justbecause

ENTRYPOINT ["/bin/bash"]
