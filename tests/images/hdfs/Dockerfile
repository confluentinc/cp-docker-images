FROM confluentinc/cp-base

ENV JAVA_HOME=/usr/lib/jvm/java-7-oracle/
ENV HADOOP_INSTALL=/opt/hadoop
ENV HADOOP_VERSION=2.7.2

RUN \
  echo "===> Install Hadoop ..." \
  && mkdir -p /opt \
  && cd /opt \
  && wget --quiet http://apache.mirrors.lucidnetworks.net/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
  && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz \
  && ln -s hadoop-${HADOOP_VERSION} hadoop \
  && export PATH=$PATH:$HADOOP_INSTALL/bin \
  && export PATH=$PATH:$HADOOP_INSTALL/sbin \
  && chmod -R ga+w /opt/hadoop/etc \
  && chmod -R ga+r /opt/hadoop \
  && rm -rf hadoop-${HADOOP_VERSION}.tar.gz \
  && mkdir -p /hdfs/data && chmod -R ag+w /hdfs

#EXPOSE 9000 50010 50020 50070 50075 50090 50475

COPY config/hadoop-env.sh $HADOOP_INSTALL/etc/hadoop/hadoop-env.sh
COPY config/logging.properties $HADOOP_INSTALL/share/hadoop/httpfs/tomcat/conf/logging.properties
COPY config/httpfs-log4j.properties $HADOOP_INSTALL/etc/hadoop/httpfs-log4j.properties

COPY start.sh /start.sh

VOLUME [ "/hdfs/data" ]

CMD ["bash" , "/start.sh"]
