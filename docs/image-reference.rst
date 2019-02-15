.. _image_reference:

Docker Image Reference
======================

.. include:: includes/image-description.rst

This table lists the available images and the Confluent software packages that they contain.  Some images are identified
as ```cp-enterprise-${component_name}```.   These images include proprietary components that must be licensed from Confluent
when deployed.

+------------------+------------------------------+------------------------------+-----------------------------------------+
| Component        | Image Name                   | Type                         | Packages Included                       |
+==================+==============================+==============================+=========================================+
| Base Image       | cp-base                      | |cos|                        | - zulu-openjdk-8                        |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Control Center   | cp-enterprise-control-center | |cpe|                        | - confluent-control-center              |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Kafka            | cp-kafka                     | |cos|                        | - confluent-kafka-*                     |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Kafka            | cp-enterprise-kafka          | |cpe|                        | - confluent-kafka-*                     |
|                  |                              |                              | - confluent-rebalancer                  |
|                  |                              |                              | - confluent-support-metrics             |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Kafka Connect    | cp-kafka-connect             | |cpe|                        | - confluent-control-center              |
|                  |                              |                              | - confluent-kafka-connect-elasticsearch |
|                  |                              |                              | - confluent-kafka-connect-gcs           |
|                  |                              |                              | - confluent-kafka-connect-hdfs          |
|                  |                              |                              | - confluent-kafka-connect-jdbc          |
|                  |                              |                              | - confluent-kafka-connect-s3            |
|                  |                              |                              | - confluent-monitoring-interceptors     |
|                  |                              |                              | - confluent-schema-registry             |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| KSQL CLI         | cp-ksql-cli                  | |cos|                        | - ksql-cli                              |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| KSQL Server      | cp-ksql-server               | |cpe|                        | - ksql-server                           |
|                  |                              |                              | - confluent-monitoring-interceptors     |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Replicator       | cp-enterprise-replicator     | |cpe|                        | - confluent-control-center              |
|                  |                              |                              | - confluent-kafka-replicator            |
|                  |                              |                              | - confluent-schema-registry             |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Replicator       | cp-enterprise-replicator     | |cpe|                        | - confluent-control-center              |
| Executable       | -executable                  |                              | - confluent-kafka-replicator            |
|                  |                              |                              | - confluent-schema-registry             |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| REST Proxy       | cp-kafka-rest                | |cos|                        | - confluent-kafka-rest                  |
+------------------+------------------------------+------------------------------+-----------------------------------------+
| Schema Registry  | cp-schema-registry           | |cos|                        | - confluent-schema-registry             |
+------------------+------------------------------+------------------------------+-----------------------------------------+

.. note:: The Kafka Connect and KSQL Server images are labeled as "Enterprise" simply because they contain Confluent monitoring interceptors.  The monitoring interceptors enable connectors and KSQL queries to collect the metrics which can be visualized in |c3|.  The Kafka Connect image includes |c3| in its entirety, while the KSQL Server image just includes the monitoring interceptors. No explicit license is required when using the Kafka Connect or the KSQL Server image on their own.

