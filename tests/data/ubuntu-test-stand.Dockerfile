FROM ubuntu:22.04

RUN apt update && apt install -y openssh-server

RUN echo "PasswordAuthentication no" | tee -a /etc/ssh/sshd_config
RUN echo "PermitRootLogin without-password" | tee -a /etc/ssh/sshd_config
RUN mkdir -p /root/.ssh
COPY id_useless.pub /root/.ssh/authorized_keys
RUN chmod 0600 /root/.ssh/authorized_keys

RUN service ssh start
EXPOSE 22
CMD ["/usr/sbin/sshd","-D"]
