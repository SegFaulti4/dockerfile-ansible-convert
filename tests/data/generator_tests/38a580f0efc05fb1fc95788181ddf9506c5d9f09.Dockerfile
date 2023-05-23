# A Data Volume Container to persist the expensively built virtualenv across
# rebuilds of the "dev" image

# Same base as dev image, to save space. (It's copy-on-write.)
FROM ubuntu-test-stand

# Match UID with dev image:
RUN mkdir /venv && chown -R 1000:1000 /venv
VOLUME /venv
