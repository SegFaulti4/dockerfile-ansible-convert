FROM ubuntu-test-stand
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "bash", "zsh", "ksh"]
