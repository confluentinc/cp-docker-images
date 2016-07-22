# Builds a docker image for Kafka Connect 

FROM confluentinc/cp-kafka

MAINTAINER contact@confluent.io

ENV COMPONENT=kafka-connect

# Default kafka-connect rest.port
EXPOSE 8083

RUN echo "===> Setting up ${COMPONENT}..." \
    && mkdir -p /etc/${COMPONENT} \
    && chmod -R ag+w /etc/${COMPONENT}

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
