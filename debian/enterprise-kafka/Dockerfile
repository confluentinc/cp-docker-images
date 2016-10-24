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

FROM confluentinc/cp-kafka

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

ENV COMPONENT=kafka

# primary
EXPOSE 9092

RUN echo "===> installing confluent-support-metrics ..." \
    && apt-get update && apt-get install -y \
          confluent-support-metrics=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION} \
          # confluent-rebalancer=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION} \
    \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    \
		&& echo "===> Setting up ${COMPONENT} dirs..." \
   	&& mkdir -p /var/lib/${COMPONENT}/data /etc/${COMPONENT}/secrets\
   	&& chmod -R ag+w /etc/${COMPONENT} /var/lib/${COMPONENT}/data /etc/${COMPONENT}/secrets

# REMOVE and uncomment the RUN command above when replicator packages are available
ENV CONFLUENT_DEB_REPO="https://s3-us-west-2.amazonaws.com/jenkins-confluent-packages/packaging-3.1.x/19"
RUN  echo "===> Adding confluent repository...${CONFLUENT_DEB_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}" \
     && echo "deb [arch=amd64] ${CONFLUENT_DEB_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION} stable main" >> /etc/apt/sources.list \
     && apt-get -qq update \
     && apt-get install -y --force-yes confluent-rebalancer=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION}


VOLUME ["/var/lib/${COMPONENT}/data", "/etc/${COMPONENT}/secrets"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
