FROM python:2.7-slim

ENV DOCKERIZE_VERSION="0.2.0"
ENV SCALA_VERSION="2.11"
ENV CONFLUENT_MAJOR_VERSION="3.0"

RUN echo "===> update debian ....." \
    && apt-get update \
    \
    && echo "===> install curl wget ...." \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
                curl \
                wget \
    && echo "===> install python packages ..."  \
    && pip install --no-cache-dir jinja2 \
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
    && export JAVA_HOME=/usr/lib/jvm/java-8-oracle \
    && rm -rf $JAVA_HOME/*src.zip  \
    && rm -rf \
            ${JAVA_HOME}/*/javaws \
            ${JAVA_HOME}/*/jjs \
            ${JAVA_HOME}/*/keytool \
            ${JAVA_HOME}/*/orbd \
            ${JAVA_HOME}/*/pack200 \
            ${JAVA_HOME}/*/policytool \
            ${JAVA_HOME}/*/rmid \
            ${JAVA_HOME}/*/rmiregistry \
            ${JAVA_HOME}/*/servertool \
            ${JAVA_HOME}/*/tnameserv \
            ${JAVA_HOME}/*/unpack200 \
            ${JAVA_HOME}/*/*javafx* \
            ${JAVA_HOME}/*/*jfx* \
            ${JAVA_HOME}/*/amd64/libdecora_sse.so \
            ${JAVA_HOME}/*/amd64/libfxplugins.so \
            ${JAVA_HOME}/*/amd64/libglass.so \
            ${JAVA_HOME}/*/amd64/libgstreamer-lite.so \
            ${JAVA_HOME}/*/amd64/libjavafx*.so \
            ${JAVA_HOME}/*/amd64/libjfx*.so \
            ${JAVA_HOME}/*/amd64/libprism_*.so \
            ${JAVA_HOME}/*/deploy* \
            ${JAVA_HOME}/*/desktop \
            ${JAVA_HOME}/*/ext/jfxrt.jar \
            ${JAVA_HOME}/*/ext/nashorn.jar \
            ${JAVA_HOME}/*/javaws.jar \
            ${JAVA_HOME}/*/jfr \
            ${JAVA_HOME}/*/jfr \
            ${JAVA_HOME}/*/jfr.jar \
            ${JAVA_HOME}/*/missioncontrol \
            ${JAVA_HOME}/*/oblique-fonts \
            ${JAVA_HOME}/*/plugin.jar \
            ${JAVA_HOME}/*/visualvm \
            ${JAVA_HOME}/man \
            ${JAVA_HOME}/plugin \
            ${JAVA_HOME}/*.txt \
            ${JAVA_HOME}/*/*/javaws \
            ${JAVA_HOME}/*/*/jjs \
            ${JAVA_HOME}/*/*/keytool \
            ${JAVA_HOME}/*/*/orbd \
            ${JAVA_HOME}/*/*/pack200 \
            ${JAVA_HOME}/*/*/policytool \
            ${JAVA_HOME}/*/*/rmid \
            ${JAVA_HOME}/*/*/rmiregistry \
            ${JAVA_HOME}/*/*/servertool \
            ${JAVA_HOME}/*/*/tnameserv \
            ${JAVA_HOME}/*/*/unpack200 \
            ${JAVA_HOME}/*/*/*javafx* \
            ${JAVA_HOME}/*/*/*jfx* \
            ${JAVA_HOME}/*/*/amd64/libdecora_sse.so \
            ${JAVA_HOME}/*/*/amd64/libfxplugins.so \
            ${JAVA_HOME}/*/*/amd64/libglass.so \
            ${JAVA_HOME}/*/*/amd64/libgstreamer-lite.so \
            ${JAVA_HOME}/*/*/amd64/libjavafx*.so \
            ${JAVA_HOME}/*/*/amd64/libjfx*.so \
            ${JAVA_HOME}/*/*/amd64/libprism_*.so \
            ${JAVA_HOME}/*/*/deploy* \
            ${JAVA_HOME}/*/*/desktop \
            ${JAVA_HOME}/*/*/ext/jfxrt.jar \
            ${JAVA_HOME}/*/*/ext/nashorn.jar \
            ${JAVA_HOME}/*/*/javaws.jar \
            ${JAVA_HOME}/*/*/jfr \
            ${JAVA_HOME}/*/*/jfr \
            ${JAVA_HOME}/*/*/jfr.jar \
            ${JAVA_HOME}/*/*/missioncontrol \
            ${JAVA_HOME}/*/*/oblique-fonts \
            ${JAVA_HOME}/*/*/plugin.jar \
            ${JAVA_HOME}/*/*/visualvm \
            ${JAVA_HOME}/*/man \
            ${JAVA_HOME}/*/plugin \
            ${JAVA_HOME}/*.txt \
    && echo "===> clean up ..."  \
    && rm -rf /var/cache/oracle-jdk8-installer \
    && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/*
