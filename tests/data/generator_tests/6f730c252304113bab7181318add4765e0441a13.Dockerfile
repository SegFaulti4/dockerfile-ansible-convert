FROM ubuntu-test-stand
LABEL maintainer "Gemfield <gemfield@civilnet.cn>"

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
	python3 \
	python3-setuptools \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*
