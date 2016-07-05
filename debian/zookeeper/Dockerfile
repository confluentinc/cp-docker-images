FROM confluentinc/base

EXPOSE 2181 2888 3888

ENV COMPONENT=zookeeper

RUN echo "===> installing ${COMPONENT}..." \
    && apt-get update && apt-get install -y confluent-kafka-${SCALA_VERSION} \
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
