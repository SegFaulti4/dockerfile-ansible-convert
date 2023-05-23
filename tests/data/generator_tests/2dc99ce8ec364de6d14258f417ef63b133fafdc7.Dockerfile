FROM ubuntu-test-stand

RUN PACKAGES="\
        rsync \
        lsyncd \
    " && \
    apt-get update && \
    apt-get install -y $PACKAGES && \
    apt-get autoremove --purge -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
