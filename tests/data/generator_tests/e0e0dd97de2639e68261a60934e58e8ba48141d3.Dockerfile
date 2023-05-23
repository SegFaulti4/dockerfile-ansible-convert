#
# Storage container for Cuckoo malware sandbox
#

FROM ubuntu-test-stand
MAINTAINER Jacob Gajek <jacob.gajek@esentire.com>

VOLUME ["/opt/sandbox/cuckoo-modified/storage"]

CMD ["/bin/true"]
