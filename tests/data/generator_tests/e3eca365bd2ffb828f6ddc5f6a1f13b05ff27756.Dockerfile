#Spark Datastore
FROM ubuntu-test-stand

RUN apt-get update

VOLUME ["/data"]

ENTRYPOINT /bin/true
