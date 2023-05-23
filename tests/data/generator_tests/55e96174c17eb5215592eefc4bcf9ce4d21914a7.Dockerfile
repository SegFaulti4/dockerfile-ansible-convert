FROM ubuntu-test-stand
MAINTAINER epheo <github@epheo.eu>

RUN apt update && apt install -y netcat

EXPOSE 1235

CMD ["env"]
