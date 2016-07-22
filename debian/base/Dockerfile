FROM debian:jessie

MAINTAINER partner-support@confluent.io

# Python
ENV PYTHON_VERSION="2.7.9-1"
ENV PYTHON_PIP_VERSION="8.1.2"

# Confluent
ENV SCALA_VERSION="2.11"
ENV CONFLUENT_MAJOR_VERSION="3.0"
ENV CONFLUENT_VERSION="3.0.0"
ENV CONFLUENT_DEB_VERSION="1"

# Zulu
ENV ZULU_OPENJDK_VERSION="8=8.15.0.1"


RUN echo "===> update debian ....." \
    && apt-get -qq update \
    \
    && echo "===> install curl wget netcat python...." \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
                curl \
                wget \
                netcat \
                python=${PYTHON_VERSION} \
    && echo "===> install python packages ..."  \
    && curl -fSL 'https://bootstrap.pypa.io/get-pip.py' | python \
    && pip install --no-cache-dir --upgrade pip==${PYTHON_PIP_VERSION} \
    && pip install --no-cache-dir jinja2 \
                                  kazoo \
                                  requests \
    \
    && echo "Installing Zulu OpenJDK ${ZULU_OPENJDK_VERSION}" \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x219BD9C9 \
    && echo "deb http://repos.azulsystems.com/debian stable  main" >> /etc/apt/sources.list.d/zulu.list \
    && apt-get -qq update \
    && apt-get -y install zulu-${ZULU_OPENJDK_VERSION} \
    && rm -rf /var/lib/apt/lists/* \
    \
    && echo "===> add confluent repository..." \
    && curl -SL http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION}/archive.key | apt-key add - \
    && echo "deb [arch=amd64] http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION} stable main" >> /etc/apt/sources.list

COPY include/dub /usr/local/bin/dub
COPY include/cub /usr/local/bin/cub
