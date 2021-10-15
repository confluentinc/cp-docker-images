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

# Builds a docker image for Replicator

FROM confluentinc/cp-kafka-connect-base

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true
ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
ARG CONFLUENT_PACKAGES_REPO
ARG CONFLUENT_MAJOR_VERSION
ARG CONFLUENT_MINOR_VERSION
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

RUN echo "===> Installing Replicator ..." \
    && echo "===> Adding confluent repository...${CONFLUENT_PACKAGES_REPO}" \
    && curl -L ${CONFLUENT_PACKAGES_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}/archive.key | apt-key add - \
    && apt-add-repository "deb [arch=amd64] ${CONFLUENT_PACKAGES_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION} stable main" \
    && apt-get update \
    && apt-get install -y \
        confluent-kafka-connect-replicator=${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL}-${CONFLUENT_DEB_VERSION} \
    && echo "===> Cleaning up ..."  \
    && apt-add-repository --remove "deb [arch=amd64] ${CONFLUENT_PACKAGES_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION} stable main" \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/*
