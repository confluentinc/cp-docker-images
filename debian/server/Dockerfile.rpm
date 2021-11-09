#
# Copyright 2019 Confluent Inc.
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

FROM confluentinc/cp-rpm-base

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER
ARG CONFLUENT_PACKAGES_REPO
ARG CONFLUENT_MAJOR_VERSION
ARG CONFLUENT_MINOR_VERSION
MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

ENV COMPONENT=kafka

# primary
EXPOSE 9092

RUN echo "===> installing ${COMPONENT}..." \
    && yum -q -y update \
    && echo "===> Adding confluent repository...${CONFLUENT_PACKAGES_REPO}" \
    && rpm --import ${CONFLUENT_PACKAGES_REPO}/rpm/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}/archive.key \
    && printf "[Confluent] \n\
name=Confluent repository \n\
baseurl=${CONFLUENT_PACKAGES_REPO}/rpm/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION} \n\
gpgcheck=1 \n\
gpgkey=${CONFLUENT_PACKAGES_REPO}/rpm/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}/archive.key \n\
enabled=1 " > /etc/yum.repos.d/confluent.repo \
    && yum install -y confluent-server-${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL} \
    && yum install -y confluent-rebalancer-${CONFLUENT_VERSION}${CONFLUENT_PLATFORM_LABEL} \
    && echo "===> clean up ..."  \
    && rm -rf /tmp/* /etc/yum.repos.d/confluent.repo \
    && echo "===> Setting up ${COMPONENT} dirs" \
    && mkdir -p /var/lib/${COMPONENT}/data /etc/${COMPONENT}/secrets \
    && chmod -R g+w /etc/kafka /var/lib/${COMPONENT}/data /etc/${COMPONENT}/secrets

VOLUME ["/var/lib/${COMPONENT}/data", "/etc/${COMPONENT}/secrets"]

COPY include/etc/confluent/docker /etc/confluent/docker

CMD ["/etc/confluent/docker/run"]
