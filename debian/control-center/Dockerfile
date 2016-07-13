# Builds a docker image for the Confluent Control Center.

FROM confluentinc/base

MAINTAINER contact@confluent.io

ENV COMPONENT=control-center

# Default listener
EXPOSE 9021

RUN echo "===> installing ${COMPONENT}..." \
    && apt-get update && apt-get install -y confluent-${COMPONENT} \
    \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && chmod -R ag+w /etc/confluent-${COMPONENT}

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
