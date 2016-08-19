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

# Builds a docker image for the Confluent Control Center.

FROM confluentinc/cp-base

# TODO - remove this
ENV CONFLUENT_VERSION=3.0.1

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

ENV COMPONENT=control-center
ENV CONTROL_CENTER_DATA_DIR=/var/lib/confluent-${COMPONENT}
ENV CONTROL_CENTER_CONFIG_DIR=/etc/confluent-${COMPONENT}

# Default listener
EXPOSE 9021

# TODO - remove this
RUN echo "===> add confluent repository..." \
    && curl -SL http://s3-us-west-2.amazonaws.com/staging-confluent-packages-3.0.1/deb/${CONFLUENT_MAJOR_VERSION}/archive.key | apt-key add - \
    && echo "deb [arch=amd64] http://s3-us-west-2.amazonaws.com/staging-confluent-packages-3.0.1/deb/${CONFLUENT_MAJOR_VERSION} stable main" >> /etc/apt/sources.list


RUN echo "===> installing ${COMPONENT}..." \
    && apt-get update && apt-get install -y confluent-${COMPONENT}=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION} \
    \
    && echo "===> clean up ..."  \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
    \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && mkdir -p "${CONTROL_CENTER_DATA_DIR}" \
    && chmod -R ag+w "${CONTROL_CENTER_CONFIG_DIR}" "${CONTROL_CENTER_DATA_DIR}"

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
