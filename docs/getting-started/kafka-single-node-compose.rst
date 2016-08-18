Using docker compose
~~~~~~~~~~~~~~~~~~~~

0. Install compose
1. Clone the repo

   ::

       git clone https://github.com/confluentinc/cp-docker-images
       cd cp-docker-images/examples/kafka-single-node

2. Start the services

   ::

       docker-compose start
       docker-compose run

   Make sure the services are up and running

   ::

       docker-compose ps

   You should see

   ::

                  Name                        Command            State   Ports
       -----------------------------------------------------------------------
       kafkasinglenode_kafka_1       /etc/confluent/docker/run   Up
       kafkasinglenode_zookeeper_1   /etc/confluent/docker/run   Up

   Check the zookeeper logs to verify that Zookeeper is healthy

   ::

       docker-compose log zookeeper | grep -i binding

   You should see message like the following

   ::

       zookeeper_1  | [2016-07-25 03:26:04,018] INFO binding to port 0.0.0.0/0.0.0.0:32181 (org.apache.zookeeper.server.NIOServerCnxnFactory)

   Check the kafka logs to verify that broker is healthy

   ::

       docker-compose log kafka | grep -i started

   You should see message like the following

   ::

       kafka_1      | [2016-07-25 03:26:06,007] INFO [Kafka Server 1], started (kafka.server.KafkaServer)

3. Follow section 3 in "Using Docker client" to test the broker.
