FROM ubuntu-test-stand

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    jq \
 && rm -rf /var/lib/apt/lists/*
