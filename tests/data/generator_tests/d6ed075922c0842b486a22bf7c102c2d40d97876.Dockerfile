FROM ubuntu-test-stand

RUN echo hello\
  world\
  goodnight  \
  moon\
  light\
ning
RUN echo hello  \
  world
RUN echo hello  \
world
RUN echo hello \
goodbye\
frog
RUN echo hi \
 \
 world \
\
 good\
\
night
RUN echo goodbye\
frog
RUN echo good\
bye\
frog

RUN echo hello \
# this is a comment that breaks escape continuation
RUN echo this is some more useful stuff
