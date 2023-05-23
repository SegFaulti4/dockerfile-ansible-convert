FROM ubuntu-test-stand
MAINTAINER Team Data Streams Core <data-streams-core@yelp.com>

RUN apt-get update && apt-get -y install zookeeper

CMD /usr/share/zookeeper/bin/zkServer.sh start-foreground
