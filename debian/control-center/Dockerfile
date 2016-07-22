# Builds a docker image for the Confluent Control Center.

FROM confluentinc/cp-base

MAINTAINER partner-support@confluent.io

ENV COMPONENT=control-center
ENV CONTROL_CENTER_DATA_DIR=/var/lib/${COMPONENT}
ENV CONTROL_CENTER_CONFIG_DIR=/etc/confluent-${COMPONENT}

# Default listener
EXPOSE 9021

RUN echo "===> installing ${COMPONENT}..." \
    && apt-get update && apt-get install -y confluent-${COMPONENT} \
    \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && mkdir -p "${CONTROL_CENTER_DATA_DIR}" \
    && chmod -R ag+w "${CONTROL_CENTER_CONFIG_DIR}" "${CONTROL_CENTER_DATA_DIR}"

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
