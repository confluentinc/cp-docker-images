FROM confluentinc/base

# primary, jmx
EXPOSE 9092 7203

RUN echo "===> add confluent repository..." \
    && curl -SL http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION}/archive.key | apt-key add - \
    && echo "deb [arch=amd64] http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION} stable main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y confluent-kafka-${SCALA_VERSION} \
    \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    \
    && echo "===> Setting up Kafka dirs" \
    && mkdir -p /opt/kafka/data \
    && chmod -R ag+w /etc/kafka /opt/kafka/data

VOLUME ["/opt/kafka/data"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
