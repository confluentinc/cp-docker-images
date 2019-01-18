# Overview

This example deploys an active-active multi-datacenter design, with two instances of Confluent Replicator copying data bi-directionally between the datacenters.
Confluent Control Center is running to manage and monitor.

This is for demo purposes only, not for production.

Here is a list of Confluent Platform services and their associated ports

|                | DC1                     | DC2                     |
|----------------|-------------------------|-------------------------|
|ZooKeeper       | 2181                    | 2182                    |
|Broker          | 9091                    | 9092                    |
|Schema Registry | 8081 (primary)          | 8082 (secondary)        |
|Connect         | 8381 (copying DC2->DC1) | 8382 (copying DC1->DC2) |
|Control Center  |                         | 9021                    |


# Data generation and topic names

There are also Docker containers with data generators that produce data to the same topic name `topic1` in each datacenter.
Confluent Replicator 5.0.1 prevents cyclic repetition of data between the DC1 `topic1` and DC2 `topic1`, by using provenance information in the message headers.

# Pre-requisites

* Docker version 17.06.1-ce
* Docker Compose version 1.14.0 with Docker Compose file format 2.1

# Running

Start all services, and print some messages from various topics in each datacenter:

```bash
./start.sh
```

Stop all services:

```bash
./stop.sh
```

# Resuming Java Consumer Applications in Failover

After a disaster event occurs, consumers can switch datacenters and automatically restart consuming data in the destination cluster where they left off in the origin cluster, a capability introduced in Confluent Platform version 5.0.

To use this capability, configure Java consumer applications with the [Consumer Timestamps Interceptor](https://docs.confluent.io/current/multi-dc-replicator/replicator-failover.html#configuring-the-consumer-for-failover), which is shown in this [sample code](https://github.com/confluentinc/examples/blob/5.0.1-post/clients/avro/src/main/java/io/confluent/examples/clients/basicavro/ConsumerMultiDatacenterExample.java).

1. After starting this Docker environment (see previous section), run the consumer to connect to DC1 Kafka cluster. It uses the consumer group id `java-consumer-app`.

```bash
git clone https://github.com/confluentinc/examples.git
cd clients/avro
mvn clean package
mvn exec:java -Dexec.mainClass=io.confluent.examples.clients.basicavro.ConsumerMultiDatacenterExample -Dexec.args="localhost:29091 http://localhost:8081 localhost:29092"
```

Verify the consumer is reading data originating from both DC1 and DC2:

```bash
...
key = User_1, value = {"userid": "User_1", "dc": "DC1"}
key = User_9, value = {"userid": "User_9", "dc": "DC2"}
key = User_6, value = {"userid": "User_6", "dc": "DC2"}
...
```

2. Even though the consumer is consuming from DC1, there are DC2 consumer offsets committed for the consumer group `java-consumer-app`.

```bash
docker-compose exec broker-dc2 kafka-console-consumer --topic __consumer_offsets --bootstrap-server localhost:29092 --formatter "kafka.coordinator.group.GroupMetadataManager\$OffsetsMessageFormatter" | grep java-consumer-app
```

You should see some offsets:

```bash
...
[java-consumer-app,topic1,0]::OffsetAndMetadata(offset=1142, leaderEpoch=Optional.empty, metadata=, commitTimestamp=1547146285084, expireTimestamp=None)
[java-consumer-app,topic1,0]::OffsetAndMetadata(offset=1146, leaderEpoch=Optional.empty, metadata=, commitTimestamp=1547146286082, expireTimestamp=None)
[java-consumer-app,topic1,0]::OffsetAndMetadata(offset=1150, leaderEpoch=Optional.empty, metadata=, commitTimestamp=1547146287084, expireTimestamp=None)
...
```

3. Shut down DC1:

```bash
docker-compose stop connect-dc1 schema-registry-dc1 broker-dc1 zookeeper-dc1
```

4. Restart the consumer to connect to DC2 Kafka cluster, still using the same consumer group id `java-consumer-app`:

```bash
mvn exec:java -Dexec.mainClass=io.confluent.examples.clients.basicavro.ConsumerMultiDatacenterExample -Dexec.args="localhost:29092 http://localhost:8082 localhost:29092"
```

You should see data sourced from only DC2:

```bash
...
key = User_8, value = {"userid": "User_8", "dc": "DC2"}
key = User_9, value = {"userid": "User_9", "dc": "DC2"}
key = User_5, value = {"userid": "User_5", "dc": "DC2"}
...
```

# Additional Reading

Whitepaper: [Disaster Recovery for Multi-Datacenter Apache Kafka Deployments](https://www.confluent.io/white-paper/disaster-recovery-for-multi-datacenter-apache-kafka-deployments/)
