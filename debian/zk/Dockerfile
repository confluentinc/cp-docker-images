FROM confluentinc/base

EXPOSE 2181 2888 3888

RUN echo "===> add confluent repository..." \
    && curl -SL http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION}/archive.key | apt-key add - \
    && echo "deb [arch=amd64] http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION} stable main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y confluent-kafka-${SCALA_VERSION} \
    \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    \
    && echo "===> Setting up ZK dirs" \
    && mkdir -p /opt/zookeeper/data /opt/zookeeper/log \
    && chmod -R a+rwx /etc/kafka /opt/zookeeper/data /opt/zookeeper/log

VOLUME ["/opt/zookeeper/data", "/opt/zookeeper/log"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
