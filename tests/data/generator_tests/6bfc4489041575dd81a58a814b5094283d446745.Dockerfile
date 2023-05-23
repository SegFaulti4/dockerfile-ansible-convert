FROM ubuntu-test-stand

RUN apt-get update
RUN apt-get install -y figlet
WORKDIR /app
RUN touch teste

ENTRYPOINT ["node"]
CMD ["app.py"]