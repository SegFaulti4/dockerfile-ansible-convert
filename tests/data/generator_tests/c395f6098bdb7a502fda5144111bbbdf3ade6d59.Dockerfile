FROM ubuntu-test-stand

# curl

RUN apt-get update \
&& apt-get install -y curl \
&& rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
