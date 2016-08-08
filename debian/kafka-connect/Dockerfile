# Builds a docker image for Kafka Connect

FROM confluentinc/cp-kafka

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true
ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

ENV COMPONENT=kafka-connect

# Default kafka-connect rest.port
EXPOSE 8083

RUN echo "===> Installing Schema Registry (for Avro jars), JDBC and Hadoop connectors ..." \
    && apt-get -qq update \
    && apt-get install -y \
        confluent-kafka-connect-jdbc=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION} \
        confluent-kafka-connect-hdfs=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION} \
        confluent-schema-registry=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION} \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    echo "===> Setting up ${COMPONENT} dirs ..." \
    && mkdir -p /etc/${COMPONENT} /etc/${COMPONENT}/secrets /etc/${COMPONENT}/jars \
    && chmod -R ag+w /etc/${COMPONENT} /etc/${COMPONENT}/secrets /etc/${COMPONENT}/jars

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
