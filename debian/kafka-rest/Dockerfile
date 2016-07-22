FROM confluentinc/cp-base

ENV COMPONENT=kafka-rest

# default listener 
EXPOSE 8082

RUN echo "===> installing ${COMPONENT}..." \
    && apt-get update && apt-get install -y confluent-${COMPONENT} \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && chmod -R ag+w /etc/${COMPONENT}

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
