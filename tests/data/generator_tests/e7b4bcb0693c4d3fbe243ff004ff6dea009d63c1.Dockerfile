FROM ubuntu-test-stand
RUN useradd -ms /bin/bash test
ENTRYPOINT ["cp", "/pfs/in/file", "/pfs/out/file"]
