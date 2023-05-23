FROM ubuntu-test-stand
entrypoint [ "setarch", "x86_64", "-R", "/usr/bin/env", "HAHAHA" ]
