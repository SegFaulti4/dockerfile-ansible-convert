FROM ubuntu-test-stand
RUN ls -la
WORKDIR /root/CbTest/
ENTRYPOINT ["./startLoader.sh"]



