How to extend the images ?
==========================

You might want to extend the images to add new software, change the
config management, use service discovery etc.

Prerequisites
-------------

1. Read the section on ``development`` to setup the development
   environment to build docker images.
2. Understand how the images are structured by reading the following
   docs:

   -  ``image-structure`` describes the structure of the images
   -  ``utility_scripts`` describes the utility scripts used in the
      images

Examples
--------

The following examples show to extend the images.

1. Download configuration from a URL

  This example shows how to change the configuration management. You will need to override the ``configure`` script to download the scripts from an HTTP URL.

  For example:

  To do this for the Zookeeper image, you will need the following dockerfile and configure script. This example assumes that each property file is has a URL.

  ``Dockerfile``

  ::

      FROM confluentinc/cp-zookeeper

      COPY include/etc/confluent/docker/configure /etc/confluent/docker/configure

  ``include/etc/confluent/docker/configure``

  ::

      set -o nounset \
          -o errexit \
          -o verbose \
          -o xtrace


      # Ensure that URL locations are available.
      dub ensure ZOOKEEPER_SERVER_CONFIG_URL
      dub ensure ZOOKEEPER_SERVER_ID_URL
      dub ensure ZOOKEEPER_LOG_CONFIG_URL

      # Ensure that the config location is writable.
      dub path /etc/kafka/ writable

      curl -XGET ZOOKEEPER_SERVER_CONFIG_URL > /etc/kafka/zookeeper.properties
      curl -XGET ZOOKEEPER_SERVER_ID_URL > /var/lib/zookeeper/data/myid
      curl -XGET ZOOKEEPER_LOG_CONFIG_URL > /etc/kafka/log4j.properties

      Build the image:

          docker build -t foo/zookeeper:latest .


  Run it :

  ::

      docker run \
           -e ZOOKEEPER_SERVER_CONFIG_URL=http://foo.com/zk1/server.properties \
           -e ZOOKEEPER_SERVER_ID_URL =http://foo.com/zk1/myid \
           -e ZOOKEEPER_LOG_CONFIG_URL =http://foo.com/zk1/log4j.properties \
           foo/zookeeper:latest

2. Add more software

  This example shows how to add new software to an image. For example, you might want to extend the Kafka Connect client to include the MySQL JDBC driver.

   ``Dockerfile``

   ::

       FROM confluentinc/cp-kafka-connect

       ENV MYSQL_DRIVER_VERSION 5.1.39

       RUN curl -k -SL "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-${MYSQL_DRIVER_VERSION}.tar.gz" \
           | tar -xzf - -C /usr/share/java/kafka/ --strip-components=1 mysql-connector-java-5.1.39/mysql-connector-java-${MYSQL_DRIVER_VERSION}-bin.jar

   Build the image:

   ::

       docker build -t foo/mysql-connect:latest .

   **This approach can also be used to create images with your own Kafka Connect Plugins.**

3. Logging to volumes

  The images only expose volumes for data and security configuration. But you might want to write to external storage for some use cases. For example: You might want to write the Kafka authorizer logs to a volume for auditing.

  ``Dockerfile``

  ::

      FROM confluentinc/cp-kafka

      # Make sure the log directory is world-writable
      RUN echo "===> Creating authorizer logs dir ..." \
           && mkdir -p /var/log/kafka-auth-logs
           && chmod -R ag+w /var/log/kafka-auth-logs

      VOLUME ["/var/lib/${COMPONENT}/data", "/etc/${COMPONENT}/secrets", "/var/log/kafka-auth-logs"]

      COPY include/etc/confluent/log4j.properties.template /etc/confluent/log4j.properties.template

  ``include/etc/confluent/log4j.properties.template``

  ::

    log4j.rootLogger={{ env["KAFKA_LOG4J_ROOT_LOGLEVEL"] | default('INFO') }}, stdout

    log4j.appender.stdout=org.apache.log4j.ConsoleAppender
    log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
    log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n

    log4j.appender.authorizerAppender=org.apache.log4j.DailyRollingFileAppender
    log4j.appender.authorizerAppender.DatePattern='.'yyyy-MM-dd-HH
    log4j.appender.authorizerAppender.File=/var/log/kafka-auth-logs/kafka-authorizer.log
    log4j.appender.authorizerAppender.layout=org.apache.log4j.PatternLayout
    log4j.appender.authorizerAppender.layout.ConversionPattern=[%d] %p %m (%c)%n

    log4j.additivity.kafka.authorizer.logger=false

    {% set loggers = {
     'kafka': 'INFO',
     'kafka.network.RequestChannel$': 'WARN',
     'kafka.producer.async.DefaultEventHandler': 'DEBUG',
     'kafka.request.logger': 'WARN',
     'kafka.controller': 'TRACE',
     'kafka.log.LogCleaner': 'INFO',
     'state.change.logger': 'TRACE',
     'kafka.authorizer.logger': 'WARN, authorizerAppender'
     } -%}


    {% if env['KAFKA_LOG4J_LOGGERS'] %}
    {% set loggers = parse_log4j_loggers(env['KAFKA_LOG4J_LOGGERS'], loggers) %}
    {% endif %}

  Build the image:

  ::

    docker build -t foo/kafka-auditable:latest .

4. Writing heap and verbose GC logging to external volumes

  You might want to log heap dumps and GC logs to an external volumes for debugging for the Kafka image.

  ``Dockerfile``

  ::

    FROM confluentinc/cp-kafka

    # Make sure the jvm log directory is world-writable
    RUN echo "===> Creating jvm logs dir ..." \
         && mkdir -p /var/log/jvm-logs
         && chmod -R ag+w /var/log/jvm-logs

    VOLUME ["/var/lib/${COMPONENT}/data", "/etc/${COMPONENT}/secrets", "/var/log/jvm-logs"]

  Build the image:

  ::

    docker build -t foo/kafka-verbose-jvm:latest .

  Run it :

  ::

    docker run \
        -e KAFKA_HEAP_OPTS="-Xmx256M -Xloggc:/var/log/jvm-logs/verbose-gc.log -verbose:gc -XX:+PrintGCDateStamps -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/log/jvm-logs" \
        foo/kafka-verbose-jvm:latest

5. External Service discovery

  You can extend the images to support for any service discovery mechanism either by overriding relevent properties or by overriding the ``configure`` script as explained in example 1.

  The images support Mesos by overriding relevent proprties for Mesos service discovery. See ``debian/kafka-connect/includes/etc/confluent/docker/mesos-overrides`` for examples.

6. Use Oracle JDK

  The images ship with Zulu OpenJDK. We cannot bundle Oracle JDK because of licensing restrictions. Follow the steps below to modify the images to include Oracle JDK instead of Zulu OpenJDK.

  1. Change the base image to install Oracle JDK instead of Zulu OpenJDK.

  ``Dockerfile``

  ::

     FROM debian:jessie

     ARG COMMIT_ID=unknown
     LABEL io.confluent.docker.git.id=$COMMIT_ID
     ARG BUILD_NUMBER=-1
     LABEL io.confluent.docker.build.number=$BUILD_NUMBER

     MAINTAINER partner-support@confluent.io
     LABEL io.confluent.docker=true


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
                                   requests \
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
     \
     && echo "===> clean up ..."  \
     && rm -rf /var/cache/oracle-jdk8-installer \
     && apt-get clean && rm -rf /tmp/* /var/lib/apt/lists/* \
     \
     \
     && echo "===> add confluent repository..." \
     && curl -SL http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION}/archive.key | apt-key add - \
     && echo "deb [arch=amd64] http://packages.confluent.io/deb/${CONFLUENT_MAJOR_VERSION} stable main" >> /etc/apt/sources.list

     COPY include/dub /usr/local/bin/dub
     COPY include/cub /usr/local/bin/cub
     COPY include/etc/confluent/docker /etc/confluent/docker


  2. Build all the images

    ::

      make build-debian
