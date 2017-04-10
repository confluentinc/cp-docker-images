# Confluent's Kafka Streams Examples

This example launches:

- Confluent's Kafka Music demo application for the Kafka Streams API.  This application demonstrates how to build of a simple music charts application.  It uses Kafka's
  [Interactive Queries](http://docs.confluent.io/current/streams/developer-guide.html#interactive-queries) feature to
  expose its latest processing results (e.g. latest Top 5 songs) via a REST API.  Its input data is in Avro format,
  hence the use of Confluent Schema Registry (see below).
- a single-node Apache Kafka cluster with a single-node ZooKeeper ensemble
- a [Confluent Schema Registry](https://github.com/confluentinc/schema-registry) instance

The Kafka Music application demonstrates how to build of a simple music charts application that continuously computes,
in real-time, the latest charts such as Top 5 songs per music genre.  It exposes its latest processing results -- the
latest charts -- via Kafka’s Interactive Queries feature and a REST API.  The application's input data is in Avro format
and comes from two sources: a stream of play events (think: "song X was played") and a stream of song metadata ("song X
was written by artist Y").

More specifically, we will run the following services:

* Confluent's Kafka Music demo application
* a single-node Kafka cluster with a single-node ZooKeeper ensemble
* Confluent Schema Registry

You can find detailed documentation at
http://docs.confluent.io/3.2.0/cp-docker-images/docs/tutorials/kafka-streams-examples.html.
