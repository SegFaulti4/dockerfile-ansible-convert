FROM ubuntu-test-stand


## installation

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
                    # basic stuff
                    curl ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/julia/usr && \
    curl -s -L https://julialangnightlies-s3.julialang.org/bin/linux/x64/julia-latest-linux64.tar.gz | tar -C /opt/julia/usr -x -z --strip-components=1 -f -


## execution

WORKDIR /

RUN ln -s /opt/julia/usr/bin/julia       /usr/bin/julia && \
    ln -s /opt/julia/usr/bin/julia-debug /usr/bin/julia-debug
