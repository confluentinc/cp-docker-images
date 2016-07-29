FROM confluentinc/cp-zookeeper

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

ENV COMPONENT=kafka

# primary
EXPOSE 9092

RUN echo "===> Setting up ${COMPONENT} dirs..." \
   && mkdir -p /var/lib/${COMPONENT}/data /etc/${COMPONENT}/secrets\
   && chmod -R ag+w /etc/${COMPONENT} /var/lib/${COMPONENT}/data /etc/${COMPONENT}/secrets


VOLUME ["/var/lib/${COMPONENT}/data", "/etc/${COMPONENT}/secrets"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
