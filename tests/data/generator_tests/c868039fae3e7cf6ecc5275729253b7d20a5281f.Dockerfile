FROM ubuntu-test-stand

ENV CNB_USER_ID=2222
ENV CNB_GROUP_ID=3333

RUN \
  groupadd pack --gid 3333 && \
  useradd --uid 2222 --gid 3333 -m -s /bin/bash pack

RUN apt-get update && apt-get -yq install netcat
LABEL io.buildpacks.stack.id=pack.test.stack

USER pack


