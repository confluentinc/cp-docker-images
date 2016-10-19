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
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

# RUN echo "===> Installing Replicator ..." \
#     && apt-get -qq update \
#     && apt-get install -y \
#         confluent-kafka-connect-replicator=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION} \
#     && echo "===> Cleaning up ..."  \
#     && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/*

# REMOVE and uncomment the RUN command above when replicator packages are available
ENV CONFLUENT_DEB_REPO="https://s3-us-west-2.amazonaws.com/jenkins-confluent-packages/packaging-3.1.x/14"
RUN  echo "===> Adding confluent repository...${CONFLUENT_DEB_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}" \
     && echo "deb [arch=amd64] ${CONFLUENT_DEB_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION} stable main" >> /etc/apt/sources.list \
     && apt-get -qq update \
     && apt-get install -y --force-yes confluent-kafka-connect-replicator=${CONFLUENT_VERSION}-${CONFLUENT_DEB_VERSION}
