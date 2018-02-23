#
# Copyright 2016 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM confluentinc/cp-base

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

ENV COMPONENT=kafka-rest

# default listener
EXPOSE 8082

RUN echo "===> installing ${COMPONENT}..." \
    && apt-get update && apt-get install -y \
        confluent-${COMPONENT}=${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL}-${CONFLUENT_DEB_VERSION} \
        confluent-control-center=${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL}-${CONFLUENT_DEB_VERSION} \
        confluent-security=${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL}-${CONFLUENT_DEB_VERSION} \
    && echo "Downloading new ZK Version ... " \
    && curl -o /tmp/zookeeper-3.4.10.1.jar http://downloads.mesosphere.com/kafka/assets/zookeeper-3.4.10.1.jar \
    && echo "===> Replacing ZK with newer version" \
    && rm -f /usr/share/java/confluent-control-center/zookeeper-3.4.10.jar \
    && rm -f /usr/share/java/schema-registry/zookeeper-3.4.10.jar \
    && rm -f /usr/share/java/confluent-serializers/zookeeper-3.4.10.jar \
    && rm -f /usr/share/java/confluent-rebalancer/zookeeper-3.4.10.jar \
    && rm -f /usr/share/java/confluent-common/zookeeper-3.4.10.jar \
    && cp /tmp/zookeeper-3.4.10.1.jar /usr/share/java/confluent-control-center \
    && cp /tmp/zookeeper-3.4.10.1.jar /usr/share/java/schema-registry \
    && cp /tmp/zookeeper-3.4.10.1.jar /usr/share/java/confluent-serializers \
    && cp /tmp/zookeeper-3.4.10.1.jar /usr/share/java/confluent-rebalancer \
    && cp /tmp/zookeeper-3.4.10.1.jar /usr/share/java/confluent-common \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && chmod -R ag+w /etc/${COMPONENT}

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
