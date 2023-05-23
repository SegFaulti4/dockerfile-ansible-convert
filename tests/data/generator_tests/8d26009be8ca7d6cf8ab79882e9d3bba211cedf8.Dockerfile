# Data-only container for annalist site data
#
# cf. 
#    http://www.tech-d.net/2013/12/16/persistent-volumes-with-docker-container-as-volume-pattern/
#    http://www.alexecollins.com/docker-persistence/
#

FROM ubuntu-test-stand

VOLUME /annalist_site

CMD ["true"]

