# Builds a docker image for Kafka Connect 

FROM confluentinc/cp-kafka

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

ENV COMPONENT=kafka-connect

# Default kafka-connect rest.port
EXPOSE 8083

RUN echo "===> Setting up ${COMPONENT}..." \
    && mkdir -p /etc/${COMPONENT} \
    && chmod -R ag+w /etc/${COMPONENT}

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
