FROM ubuntu-test-stand

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["exit 123", "# override me"]