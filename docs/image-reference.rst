.. _image_reference:

Docker Image Reference
======================

Images are available on `DockerHub <https://hub.docker.com/u/confluentinc/>`_ for each component of the |cp|. The source
files for the images are `available on GitHub <https://github.com/confluentinc/cp-docker-images>`_. From GitHub you can
extend and rebuild the images and upload them to your own DockerHub repository.

This table lists the available images and the Confluent software packages that they contain.  Some images are identified
as ```cp-enterprise-${component_name}```.   These images include proprietary components that must be licensed from Confluent
when deployed.

+------------------+------------------------------+------------------------------+-----------------------------------------+
| Component        | Image Name                   | License                      | Packages Included                       |
+==================+==============================+==============================+=========================================+
| Base Image       | cp-base                      | |community-license|          | - zulu-openjdk-8                        |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Control Center   | cp-enterprise-control-center | |commercial-license|         | - confluent-control-center              |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Kafka            | cp-kafka                     | |community-license|          | - confluent-kafka-*                     |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Kafka            | cp-enterprise-kafka          | |commercial-license|         | - confluent-kafka-*                     |
|                  |                              |                              | - confluent-rebalancer                  |
|                  |                              |                              | - confluent-support-metrics             |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| KSQL CLI         | cp-ksql-cli                  | |community-license|          | - ksql-cli                              |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Kafka Connect    | cp-kafka-connect             | |commercial-license|         | - confluent-kafka-connect-jdbc          |
|                  |                              |                              | - confluent-kafka-connect-hdfs          |
|                  |                              |                              | - confluent-schema-registry             |
|                  |                              |                              | - confluent-control-center              |
|                  |                              |                              | - confluent-kafka-connect-elasticsearch |
|                  |                              |                              | - confluent-kafka-connect-s3            |
|                  |                              |                              | - confluent-kafka-connect-gcs           |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| KSQL Server      | cp-ksql-server               | |commercial-license|         | - ksql-server                           |
|                  |                              |                              | - confluent-monitoring-interceptors     |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Replicator       | cp-enterprise-replicator     | |commercial-license|         | - confluent-kafka-replicator            |
|                  |                              |                              | - confluent-schema-registry             |
|                  |                              |                              | - confluent-control-center              |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Replicator       | cp-enterprise-replicator     | |commercial-license|         | - confluent-kafka-replicator            |
| Executable       | -executable                  |                              | - confluent-schema-registry             |
|                  |                              |                              | - confluent-control-center              |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| REST Proxy       | cp-kafka-rest                | |community-license|          | - confluent-kafka-rest                  |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Schema Registry  | cp-schema-registry           | |community-license|          | - confluent-schema-registry             |
+------------------+------------------------------+------------------------------+-----------------------------------------+

* Note: The Kafka Connect and KSQL Server images are labeled as "Enterprise" simply because they contain Confluent monitoring interceptors.  The monitoring interceptors enable connectors and KSQL queries to collect the metrics which can be visualized in Confluent Control Center.  The Kafka Connect image includes Confluent Control Center in its entirety, while the KSQL Server image just includes the monitoring interceptors. No explicit license is required when using the Kafka Connect or the KSQL Server image on their own.

