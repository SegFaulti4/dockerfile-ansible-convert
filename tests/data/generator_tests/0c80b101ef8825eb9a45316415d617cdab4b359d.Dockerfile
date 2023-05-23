FROM ubuntu-test-stand

# wget

RUN apt-get update \
&& apt-get install -y wget \
&& rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
