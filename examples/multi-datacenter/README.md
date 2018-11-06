# Overview

This example deploys an active-active multi-datacenter design.
It is for demo only, not for production.

Here is a list of Confluent Platform services and their associated ports

|                | DC1                     | DC2                     |
|----------------|-------------------------|-------------------------|
|ZooKeeper       | 2181                    | 2182                    |
|Broker          | 9091                    | 9092                    |
|Schema Registry | 8081 (primary)          | 8082 (secondary)        |
|Replicator      | 8381 (copying DC2->DC1) | 8382 (copying DC1->DC2) |

# Data generation and topic names

There are also Docker containers with data generators that populate the topic `topic1` in each datacenter.
Confluent Replicator 5.1 prevents cyclic repetition of data between the DC1 `topic1` and DC2 `topic1`, by using provenance information in the message headers.

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
