# Overview

This example setups an active-active multi-datacenter design.

DC1 has:

* 1 ZooKeeper
* 1 Broker
* 1 Schema Registry (primary)
* 1 Confluent Replicator copying data from DC2 to DC1

DC2 has:

* 1 ZooKeeper
* 1 Broker
* 1 Schema Registry (secondary)
* 1 Confluent Replicator copying data from DC1 to DC2

# Pre-requisites

* Docker version 17.06.1-ce
* Docker Compose version 1.14.0 with Docker Compose file format 2.1

# Running

Start everything, including data generation that populates the topic `topic1`:

```bash
./start.sh
```

Stop everything:

```bash
./stop.sh
```
