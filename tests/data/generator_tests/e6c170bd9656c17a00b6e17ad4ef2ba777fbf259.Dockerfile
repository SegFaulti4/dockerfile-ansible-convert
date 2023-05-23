FROM ubuntu-test-stand
ENTRYPOINT ["top", "-b"]
CMD ["-c"]
