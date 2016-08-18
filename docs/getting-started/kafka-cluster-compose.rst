Using docker compose
~~~~~~~~~~~~~~~~~~~~

0. Install compose
1. Clone the repo

   ::

       git clone https://github.com/confluentinc/cp-docker-images
       cd cp-docker-images/examples/kafka-cluster

2. Start the services

   ::

       docker-compose start
       docker-compose run

   Make sure the services are up and running

   ::

       docker-compose ps

   You should see

   ::

              Name                       Command            State   Ports
       ----------------------------------------------------------------------
       kafkacluster_kafka-1_1       /etc/confluent/docker/run   Up
       kafkacluster_kafka-2_1       /etc/confluent/docker/run   Up
       kafkacluster_kafka-3_1       /etc/confluent/docker/run   Up
       kafkacluster_zookeeper-1_1   /etc/confluent/docker/run   Up
       kafkacluster_zookeeper-2_1   /etc/confluent/docker/run   Up
       kafkacluster_zookeeper-3_1   /etc/confluent/docker/run   Up

   Check the zookeeper logs to verify that Zookeeper is healthy. For
   example, for service zookeeper-1

   ::

       docker-compose log zookeeper-1

   You should see messages like the following

   ::

       zookeeper-1_1  | [2016-07-25 04:58:12,901] INFO Created server with tickTime 2000 minSessionTimeout 4000 maxSessionTimeout 40000 datadir /var/lib/zookeeper/log/version-2 snapdir /var/lib/zookeeper/data/version-2 (org.apache.zookeeper.server.ZooKeeperServer)
       zookeeper-1_1  | [2016-07-25 04:58:12,902] INFO FOLLOWING - LEADER ELECTION TOOK - 235 (org.apache.zookeeper.server.quorum.Learner)

   Verify that ZK ensemble is ready

   ::

       for i in 22181 32181 42181; do
          docker run --net=host --rm confluentinc/cp-zookeeper:3.0.0 bash -c "echo stat | nc localhost $i | grep Mode"
       done

   You should see one ``leader`` and two ``follower``

   ::

       Mode: follower
       Mode: leader
       Mode: follower

   Check the logs to see the broker has booted up successfully

   ::

       docker-compose logs kafka-1
       docker-compose logs kafka-2
       docker-compose logs kafka-3

   You should see start see bootup messages. For example,
   ``docker-compose logs kafka-3 | grep started`` shows the following

   ::

       kafka-3_1      | [2016-07-25 04:58:15,189] INFO [Kafka Server 3], started (kafka.server.KafkaServer)
       kafka-3_1      | [2016-07-25 04:58:15,189] INFO [Kafka Server 3], started (kafka.server.KafkaServer)

   You should see the messages like the following on the broker acting
   as controller.

   ::

       (Tip: `docker-compose log | grep controller` makes it easy to grep through logs for all services.)

       kafka-3_1      | [2016-07-25 04:58:15,369] INFO [Controller-3-to-broker-2-send-thread], Controller 3 connected to localhost:29092 (id: 2 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
       kafka-3_1      | [2016-07-25 04:58:15,369] INFO [Controller-3-to-broker-2-send-thread], Controller 3 connected to localhost:29092 (id: 2 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
       kafka-3_1      | [2016-07-25 04:58:15,369] INFO [Controller-3-to-broker-1-send-thread], Controller 3 connected to localhost:19092 (id: 1 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
       kafka-3_1      | [2016-07-25 04:58:15,369] INFO [Controller-3-to-broker-1-send-thread], Controller 3 connected to localhost:19092 (id: 1 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
       kafka-3_1      | [2016-07-25 04:58:15,369] INFO [Controller-3-to-broker-1-send-thread], Controller 3 connected to localhost:19092 (id: 1 rack: null) for sending state change requests (kafka.controller.RequestSendThread)

3. Follow section 3 in "Using Docker client" to test the broker.
