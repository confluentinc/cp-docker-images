FROM confluentinc/cp-base

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER
LABEL io.confluent.docker=true

WORKDIR /opt

RUN wget http://downloads.sourceforge.net/project/cyclops-group/jmxterm/1.0-alpha-4/jmxterm-1.0-alpha-4-uber.jar -O /opt/jmxterm-1.0-alpha-4-uber.jar
