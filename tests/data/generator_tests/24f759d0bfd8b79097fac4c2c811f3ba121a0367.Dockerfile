FROM ubuntu-test-stand
# ARG must be after "FROM"
ARG BUILD_ARG
RUN echo "The value of BUILD ARG is: $BUILD_ARG"
