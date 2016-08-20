#! /bin/bash
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -o nounset \
    -o errexit \
    -o verbose \
    -o xtrace

    ps ax | grep -i 'io.confluent.admin.utils.EmbeddedKafkaCluster' | grep -v grep | awk '{print $1}' | xargs kill -SIGTERM

mvn clean compile package assembly:single -DskipTests=true

export JAAS_CONF=/tmp/jaas.conf
export MINI_KDC_DIR=/tmp/minikdc

rm -rf "$MINI_KDC_DIR" && mkdir -p "$MINI_KDC_DIR"

java -cp target/docker-utils-1.0.0-SNAPSHOT-tests.jar:$( mvn dependency:build-classpath | grep -v INFO) \
    io.confluent.admin.utils.EmbeddedKafkaCluster \
    3 \
    3 \
    true \
    /tmp/client.properties \
    "$JAAS_CONF" \
    "$MINI_KDC_DIR" &>/tmp/test-kafka-cluster.log &

KAFKA_PID=$!

echo "Kafka : $KAFKA_PID"

(java -jar target/docker-utils-1.0.0-SNAPSHOT-jar-with-dependencies.jar || exit 0)

java -Djava.security.auth.login.config="$JAAS_CONF" \
     -Djava.security.krb5.conf="$MINI_KDC_DIR/krb5.conf" \
     -jar target/docker-utils-1.0.0-SNAPSHOT-jar-with-dependencies.jar \
     zk-ready \
     localhost:11117 \
     30000 &> /tmp/test-zookeeper-ready.log

ZOOKEEPER_TEST=$([ $? -eq 0 ] && echo "PASS" || echo "FAIL")

java -Djava.security.auth.login.config="$JAAS_CONF" \
     -Djava.security.krb5.conf="$MINI_KDC_DIR/krb5.conf" \
     -jar target/docker-utils-1.0.0-SNAPSHOT-jar-with-dependencies.jar  \
     kafka-ready \
     3 \
     30000 \
     -b localhost:49092 \
     --config /tmp/client.properties &> /tmp/test-kafka-ready.log

KAFKA_BROKER_OPTION_TEST=$([ $? -eq 0 ] && echo "PASS" || echo "FAIL")

java -Djava.security.auth.login.config="$JAAS_CONF" \
     -Djava.security.krb5.conf="$MINI_KDC_DIR/krb5.conf" \
     -jar target/docker-utils-1.0.0-SNAPSHOT-jar-with-dependencies.jar  \
     kafka-ready \
     3 \
     30000 \
     -z localhost:11117 \
     -s SASL_SSL \
     --config /tmp/client.properties &> /tmp/test-kafka-zk-ready.log

KAFKA_ZK_OPTION_TEST=$([ $? -eq 0 ] && echo "PASS" || echo "FAIL")

kill "$KAFKA_PID"

echo "TEST RESULTS:"
echo "ZOOKEEPER_TEST=$ZOOKEEPER_TEST"
echo "KAFKA_ZK_OPTION_TEST=$KAFKA_ZK_OPTION_TEST"
echo "KAFKA_BROKER_OPTION_TEST=$KAFKA_BROKER_OPTION_TEST"