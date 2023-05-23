# ch-test-scope: full
FROM ubuntu-test-stand

RUN    apt-get update \
    && apt-get install -y bc \
    && rm -rf /var/lib/apt/lists/*
