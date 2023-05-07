FROM ubuntu-test-stand

RUN apt-get update && apt-get -y install zookeeper

CMD rm -rf /tmp/zookeeper && /usr/share/zookeeper/bin/zkServer.sh start-foreground
