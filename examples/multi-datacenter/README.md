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

There are also Docker containers with data generators that populate the topic `topic1` in each datacenter.


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
