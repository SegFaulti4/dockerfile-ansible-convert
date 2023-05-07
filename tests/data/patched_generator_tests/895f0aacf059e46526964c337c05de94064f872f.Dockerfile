FROM ubuntu-test-stand

ENV JAVA_HOME=/opt/java-bin
EXPOSE 8080

CMD /tomcat-bin/bin/catalina.sh run

