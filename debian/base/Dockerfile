FROM debian:jessie

ENV DOCKERIZE_VERSION="0.2.0"
ENV SCALA_VERSION="2.11"
ENV CONFLUENT_MAJOR_VERSION="3.0"

RUN echo "===> update ubuntu 15.10 ....." \
    && apt-get update \
    \
    && echo "===> install curl wget ...." \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
                curl \
                wget \
    \
    && echo "===> install dockerize ..." \
    && cd /tmp \
    && curl -L "https://github.com/jwilder/dockerize/releases/download/v$DOCKERIZE_VERSION/dockerize-linux-amd64-v$DOCKERIZE_VERSION.tar.gz" -o dockerize-linux-amd64-v$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v$DOCKERIZE_VERSION.tar.gz \
    \
    && echo "===> add webupd8 repository ..."  \
    && echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list \
    && echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886 \
    && apt-get update \
    \
    && echo "===> install Oracle Java 8 ..."   \
    && echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections \
    && echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections \
    && DEBIAN_FRONTEND=noninteractive  apt-get install -y --force-yes \
                    oracle-java8-installer \
                    oracle-java8-set-default  \
                    ca-certificates \
    && echo "===> add confluent repository..." \
    && curl -SL http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION}/archive.key | apt-key add - \
    && echo "deb [arch=amd64] http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION} stable main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y confluent-platform-${SCALA_VERSION} \
    \
    && echo "===> clean up ..."  \
    && rm -rf /var/cache/oracle-jdk8-installer \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/*
