FROM ubuntu-test-stand

# Add VOLUMEs to allow backup of logs and a shared gem repository
VOLUME  ["/gems"]

CMD /bin/bash
