FROM debian:stretch-slim

ENV GOSU_VERSION 1.7
RUN apt update \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& apt update
