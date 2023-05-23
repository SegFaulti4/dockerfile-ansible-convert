FROM ubuntu-test-stand
RUN apt-get update && apt-get -y install rsync
CMD /bin/bash /OnlineJudge/dockerfiles/test_case_rsync/run.sh
