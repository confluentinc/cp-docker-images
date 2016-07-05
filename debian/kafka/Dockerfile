FROM confluentinc/zookeeper

ENV COMPONENT=kafka

# primary, jmx
EXPOSE 9092 7203

RUN echo "===> Installing ${COMPONENT}..." \
   && mkdir -p /opt/${COMPONENT}/data \
   && chmod -R ag+w /etc/${COMPONENT} /opt/${COMPONENT}/data

VOLUME ["/opt/${COMPONENT}/data"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
