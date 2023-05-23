FROM ubuntu-test-stand
RUN mkdir /youtrack-data && touch /youtrack-data/.keep
VOLUME /youtrack-data

CMD echo "Pure data container"
