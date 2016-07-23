FROM confluentinc/cp-base

EXPOSE 2181 2888 3888

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

ENV COMPONENT=zookeeper
ENV KAFKA_VERSION="0.10.0.0"

RUN echo "===> installing ${COMPONENT}..." \
    && apt-get update && apt-get install -y confluent-kafka-${SCALA_VERSION}=${KAFKA_VERSION}-${CONFLUENT_DEB_VERSION} \
    \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && mkdir -p /opt/${COMPONENT}/data /opt/${COMPONENT}/log \
    && chmod -R ag+w /etc/kafka /opt/${COMPONENT}/data /opt/${COMPONENT}/log

VOLUME ["/opt/${COMPONENT}/data", "/opt/${COMPONENT}/log"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
