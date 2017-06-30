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

FROM debian:jessie

ARG COMMIT_ID=unknown
LABEL io.confluent.docker.git.id=$COMMIT_ID
ARG BUILD_NUMBER=-1
LABEL io.confluent.docker.build.number=$BUILD_NUMBER

# ARG CONFLUENT_DEB_REPO="http://packages.confluent.io"
ARG CONFLUENT_DEB_REPO="https://s3-us-west-2.amazonaws.com/jenkins-confluent-packages/packaging-3.3.x/37"

# Set this to false for public releases
ARG APT_ALLOW_UNAUTHENTICATED=true
#Set an env var so that it's available in derived images
ENV APT_ALLOW_UNAUTHENTICATED=${APT_ALLOW_UNAUTHENTICATED}

MAINTAINER partner-support@confluent.io
LABEL io.confluent.docker=true

# Python
ENV PYTHON_VERSION="2.7.9-1"
ENV PYTHON_PIP_VERSION="8.1.2"

# Confluent
ENV SCALA_VERSION="2.11"
ENV CONFLUENT_MAJOR_VERSION="3"
ENV CONFLUENT_MINOR_VERSION="3"

ENV CONFLUENT_PATCH_VERSION="0~SNAPSHOT"
ENV CONFLUENT_VERSION="$CONFLUENT_MAJOR_VERSION.$CONFLUENT_MINOR_VERSION.$CONFLUENT_PATCH_VERSION"
ENV CONFLUENT_DEB_VERSION="1"

# Add ~SNAPSHOT (with tilde) for internal releases
ENV KAFKA_VERSION="0.11.0.0~SNAPSHOT"

# Zulu
ENV ZULU_OPENJDK_VERSION="8=8.17.0.3"

# This affects how strings in Java class files are interpreted.  We want UTF-8 and this is the only locale in the
# base image that supports it
ENV LANG="C.UTF-8"

RUN echo "===> Updating debian ....." \
    && apt-get -qq update \
    \
    && echo "===> Installing curl wget netcat python...." \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
                apt-transport-https \
                curl \
                wget \
                netcat \
                python=${PYTHON_VERSION} \
    && echo "===> Installing python packages ..."  \
    && curl -fSL "https://bootstrap.pypa.io/get-pip.py" | python \
    && pip install --no-cache-dir --upgrade pip==${PYTHON_PIP_VERSION} \
    && pip install --no-cache-dir jinja2 \
                                  requests \
    \
    && echo "Installing Zulu OpenJDK ${ZULU_OPENJDK_VERSION}" \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x219BD9C9 \
    && echo "deb http://repos.azulsystems.com/debian stable  main" >> /etc/apt/sources.list.d/zulu.list \
    && apt-get -qq update \
    && apt-get -y install zulu-${ZULU_OPENJDK_VERSION} \
    && rm -rf /var/lib/apt/lists/* \
    && echo "===> Adding confluent repository...${CONFLUENT_DEB_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}" \
    && if [ "x$APT_ALLOW_UNAUTHENTICATED" = "xtrue" ]; then echo "APT::Get::AllowUnauthenticated \"true\";" > /etc/apt/apt.conf.d/allow_unauthenticated; else curl -L ${CONFLUENT_DEB_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION}/archive.key | apt-key add - ; fi \
    && echo "deb [arch=amd64] ${CONFLUENT_DEB_REPO}/deb/${CONFLUENT_MAJOR_VERSION}.${CONFLUENT_MINOR_VERSION} stable main" >> /etc/apt/sources.list

COPY include/dub /usr/local/bin/dub
COPY include/cub /usr/local/bin/cub
COPY include/etc/confluent/docker /etc/confluent/docker
