#
# Description : conteneur pour faire son propre CA
#
# Autheur : Thomas Boutry <thomas.boutry@x3rus.com>
#
##############

FROM ubuntu-test-stand

RUN apt-get update && \
    apt-get install -y openssl vim
