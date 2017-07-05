#
# Copyright 2017 Confluent Inc.
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

# Builds a docker image for Confluent's example applications for the Kafka Streams API

FROM confluentinc/cp-base

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true
ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

WORKDIR /build
ENV COMPONENT=kafka-streams-examples

ENV CONFLUENT_MAJOR_VERSION="3"
ENV CONFLUENT_MINOR_VERSION="3"
ENV CONFLUENT_PATCH_VERSION="0"
ENV CONFLUENT_VERSION="${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}.${CONFLUENT_PATCH_VERSION}"

# We run the Kafka Streams demo application as a non-priviledged user.
ENV STREAMS_USER="streams"
ENV STREAMS_GROUP=$STREAMS_USER

ENV STREAMS_EXAMPLES_BRANCH="${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}.x"
ENV STREAMS_EXAMPLES_FATJAR="streams-examples-${CONFLUENT_VERSION}-SNAPSHOT-standalone.jar"
ENV STREAMS_APP_DIRECTORY="/app"
ENV STREAMS_EXAMPLES_FATJAR_DEPLOYED="$STREAMS_APP_DIRECTORY/$STREAMS_EXAMPLES_FATJAR"
ENV KAFKA_MUSIC_APP_CLASS="io.confluent.examples.streams.interactivequeries.kafkamusic.KafkaMusicExample"
ENV KAFKA_MUSIC_APP_REST_HOST=localhost
ENV KAFKA_MUSIC_APP_REST_PORT=7070

EXPOSE $KAFKA_MUSIC_APP_REST_PORT

# This affects how strings in Java class files are interpreted.  We want UTF-8, and this is the only locale in the
# base image that supports it
ENV LANG="C.UTF-8"

COPY settings.xml /root/.m2/settings.xml

ENV BUILD_PACKAGES="git maven"
RUN echo "===> Installing packages to build Confluent demo applications" \
    && apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y $BUILD_PACKAGES \
    && echo "===> Building Confluent demo applications for Kafka Streams API (github.com/confluentinc/examples) ..." \
    && git clone https://github.com/confluentinc/examples \
    && cd examples/kafka-streams \
    && git checkout $STREAMS_EXAMPLES_BRANCH \
    && mvn -DskipTests=true clean package \
    && echo "===> Moving fat jar to application directory ${STREAMS_APP_DIRECTORY} ..." \
    && mkdir -p $STREAMS_APP_DIRECTORY \
    && chmod 0755 $STREAMS_APP_DIRECTORY \
    && mv -f target/$STREAMS_EXAMPLES_FATJAR $STREAMS_APP_DIRECTORY \
    && echo "===> Setting up ${COMPONENT} dirs ..." \
    && mkdir -p /etc/"${COMPONENT}" \
    && chmod ag+w /etc/"${COMPONENT}" \
    && echo "===> Cleaning up ..."  \
    && apt-get remove --purge -y $BUILD_PACKAGES \
    && apt-get clean && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* \
    && rm /root/.m2/settings.xml

COPY include/etc/confluent/docker /etc/confluent/docker

RUN groupadd $STREAMS_GROUP && useradd -r -g $STREAMS_GROUP $STREAMS_USER

USER $STREAMS_USER

CMD ["/etc/confluent/docker/run"]
