# Overview

This example deploys an active-active multi-datacenter design, with two instances of Confluent Replicator copying data bi-directionally between the datacenters.
This is for demo purposes only, not for production.

Here is a list of Confluent Platform services and their associated ports

|                | DC1                     | DC2                     |
|----------------|-------------------------|-------------------------|
|ZooKeeper       | 2181                    | 2182                    |
|Broker          | 9091                    | 9092                    |
|Schema Registry | 8081 (primary)          | 8082 (secondary)        |
|Replicator      | 8381 (copying DC2->DC1) | 8382 (copying DC1->DC2) |

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

# Java Consumer Applications

After a disaster event occurs, consumers can switch datacenters and automatically restart consuming data in the destination cluster where they left off in the origin cluster, a capability introduced in Confluent Platform version 5.0.
To use this capability, configure Java consumer applications with an interceptor called link:https://docs.confluent.io/current/multi-dc-replicator/replicator-failover.html#configuring-the-consumer-for-failover[Consumer Timestamps Interceptor], which is shown in this [sample code](https://github.com/confluentinc/examples/blob/5.0.1-post/clients/avro/src/main/java/io/confluent/examples/clients/basicavro/ConsumerMultiDatacenterExample.java).
Run the consumer as shown below:

```bash
git clone https://github.com/confluentinc/examples.git
cd clients/avro
mvn clean package
mvn exec:java -Dexec.mainClass=io.confluent.examples.clients.basicavro.ConsumerMultiDatacenterExample
```

# Additional Reading

Whitepaper: [Disaster Recovery for Multi-Datacenter Apache Kafka Deployments](https://www.confluent.io/white-paper/disaster-recovery-for-multi-datacenter-apache-kafka-deployments/)
