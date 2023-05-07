# Set the base image to Ubuntu 14.04
FROM ubuntu-test-stand
# File Author / Maintainer
MAINTAINER Laurent Jourdren <jourdren@biologie.ens.fr>

# Install Blast 2
RUN apt-get update && apt-get install --yes ncbi-blast+
