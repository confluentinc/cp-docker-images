FROM confluentinc/zookeeper

ENV COMPONENT=kafka

# primary, jmx
EXPOSE 9092 7203

RUN echo "===> Setting up ${COMPONENT} dirs..." \
   && mkdir -p /opt/${COMPONENT}/data /etc/${COMPONENT}/secrets\
   && chmod -R ag+w /etc/${COMPONENT} /opt/${COMPONENT}/data /etc/${COMPONENT}/secrets


VOLUME ["/opt/${COMPONENT}/data", "/etc/${COMPONENT}/secrets"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
