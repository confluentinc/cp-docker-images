.. _clustered_deployment_ssl:

Clustered Deployment Using SSL on Docker
========================================

This tutorial runs a secure three-node Kafka cluster and |zk| ensemble with SSL.  By the end of this tutorial, you will have successfully installed and run a simple deployment with SSL security enabled on Docker.

.. include:: includes/docker-tutorials.rst
    :end-before: setting-up-3-node

.. _docker-client-setup-3-node-ssl:

.. include:: includes/docker-tutorials.rst
    :start-after: setting-up-3-node

#. .. include:: ../includes/create-secret.rst

#. Start Up a 3-node |zk| Ensemble by running the three commands below.

   .. codewithvars:: bash

     docker run -d \
         --net=host \
         --name=zk-1 \
         -e ZOOKEEPER_SERVER_ID=1 \
         -e ZOOKEEPER_CLIENT_PORT=22181 \
         -e ZOOKEEPER_TICK_TIME=2000 \
         -e ZOOKEEPER_INIT_LIMIT=5 \
         -e ZOOKEEPER_SYNC_LIMIT=2 \
         -e ZOOKEEPER_SERVERS="localhost:22888:23888;localhost:32888:33888;localhost:42888:43888" \
         confluentinc/cp-zookeeper:|release|

   .. codewithvars:: bash

     docker run -d \
         --net=host \
         --name=zk-2 \
         -e ZOOKEEPER_SERVER_ID=2 \
         -e ZOOKEEPER_CLIENT_PORT=32181 \
         -e ZOOKEEPER_TICK_TIME=2000 \
         -e ZOOKEEPER_INIT_LIMIT=5 \
         -e ZOOKEEPER_SYNC_LIMIT=2 \
         -e ZOOKEEPER_SERVERS="localhost:22888:23888;localhost:32888:33888;localhost:42888:43888" \
         confluentinc/cp-zookeeper:|release|

   .. codewithvars:: bash

     docker run -d \
         --net=host \
         --name=zk-3 \
         -e ZOOKEEPER_SERVER_ID=3 \
         -e ZOOKEEPER_CLIENT_PORT=42181 \
         -e ZOOKEEPER_TICK_TIME=2000 \
         -e ZOOKEEPER_INIT_LIMIT=5 \
         -e ZOOKEEPER_SYNC_LIMIT=2 \
         -e ZOOKEEPER_SERVERS="localhost:22888:23888;localhost:32888:33888;localhost:42888:43888" \
         confluentinc/cp-zookeeper:|release|

   Check the logs to confirm that the |zk| servers have booted up successfully:

   .. codewithvars:: bash

     docker logs zk-1

   You should see messages like this at the end of the log output:

   .. codewithvars:: bash

     [2016-07-24 07:17:50,960] INFO Created server with tickTime 2000 minSessionTimeout 4000 maxSessionTimeout 40000 datadir /var/lib/zookeeper/log/version-2 snapdir /var/lib/zookeeper/data/version-2 (org.apache.zookeeper.server.ZooKeeperServer)
     [2016-07-24 07:17:50,961] INFO FOLLOWING - LEADER ELECTION TOOK - 21823 (org.apache.zookeeper.server.quorum.Learner)
     [2016-07-24 07:17:50,983] INFO Getting a diff from the leader 0x0 (org.apache.zookeeper.server.quorum.Learner)
     [2016-07-24 07:17:50,986] INFO Snapshotting: 0x0 to /var/lib/zookeeper/data/version-2/snapshot.0 (org.apache.zookeeper.server.persistence.FileTxnSnapLog)
     [2016-07-24 07:17:52,803] INFO Received connection request /127.0.0.1:50056 (org.apache.zookeeper.server.quorum.QuorumCnxManager)
     [2016-07-24 07:17:52,806] INFO Notification: 1 (message format version), 3 (n.leader), 0x0 (n.zxid), 0x1 (n.round), LOOKING (n.state), 3 (n.sid), 0x0 (n.peerEpoch) FOLLOWING (my state) (org.apache.zookeeper.server.quorum.FastLeaderElection)

   You can repeat the command for the two other |zk| nodes.  Next, you should verify that ZK ensemble is ready:

   .. codewithvars:: bash

     for i in 22181 32181 42181; do
        docker run --net=host --rm confluentinc/cp-zookeeper:|release| bash -c "echo stat | nc localhost $i | grep Mode"
     done

   You should see one ``leader`` and two ``follower`` instances.

   .. codewithvars:: bash

     Mode: follower
     Mode: leader
     Mode: follower

#. Now that |zk| is up and running, you can start a three node Kafka cluster.

   .. codewithvars:: bash

    docker run -d \
       --net=host \
       --name=kafka-ssl-1 \
       -e KAFKA_ZOOKEEPER_CONNECT=localhost:22181,localhost:32181,localhost:42181 \
       -e KAFKA_ADVERTISED_LISTENERS=SSL://localhost:29092 \
       -e KAFKA_SSL_KEYSTORE_FILENAME=kafka.broker1.keystore.jks \
       -e KAFKA_SSL_KEYSTORE_CREDENTIALS=broker1_keystore_creds \
       -e KAFKA_SSL_KEY_CREDENTIALS=broker1_sslkey_creds \
       -e KAFKA_SSL_TRUSTSTORE_FILENAME=kafka.broker1.truststore.jks \
       -e KAFKA_SSL_TRUSTSTORE_CREDENTIALS=broker1_truststore_creds \
       -e KAFKA_SECURITY_INTER_BROKER_PROTOCOL=SSL \
       -v ${KAFKA_SSL_SECRETS_DIR}:/etc/kafka/secrets \
       confluentinc/cp-kafka:|release|

   .. codewithvars:: bash

    docker run -d \
       --net=host \
       --name=kafka-ssl-2 \
       -e KAFKA_ZOOKEEPER_CONNECT=localhost:22181,localhost:32181,localhost:42181 \
       -e KAFKA_ADVERTISED_LISTENERS=SSL://localhost:39092 \
       -e KAFKA_SSL_KEYSTORE_FILENAME=kafka.broker2.keystore.jks \
       -e KAFKA_SSL_KEYSTORE_CREDENTIALS=broker2_keystore_creds \
       -e KAFKA_SSL_KEY_CREDENTIALS=broker2_sslkey_creds \
       -e KAFKA_SSL_TRUSTSTORE_FILENAME=kafka.broker2.truststore.jks \
       -e KAFKA_SSL_TRUSTSTORE_CREDENTIALS=broker2_truststore_creds \
       -e KAFKA_SECURITY_INTER_BROKER_PROTOCOL=SSL \
       -v ${KAFKA_SSL_SECRETS_DIR}:/etc/kafka/secrets \
       confluentinc/cp-kafka:|release|

   .. codewithvars:: bash

    docker run -d \
       --net=host \
       --name=kafka-ssl-3 \
       -e KAFKA_ZOOKEEPER_CONNECT=localhost:22181,localhost:32181,localhost:42181 \
       -e KAFKA_ADVERTISED_LISTENERS=SSL://localhost:49092 \
       -e KAFKA_SSL_KEYSTORE_FILENAME=kafka.broker3.keystore.jks \
       -e KAFKA_SSL_KEYSTORE_CREDENTIALS=broker3_keystore_creds \
       -e KAFKA_SSL_KEY_CREDENTIALS=broker3_sslkey_creds \
       -e KAFKA_SSL_TRUSTSTORE_FILENAME=kafka.broker3.truststore.jks \
       -e KAFKA_SSL_TRUSTSTORE_CREDENTIALS=broker3_truststore_creds \
       -e KAFKA_SECURITY_INTER_BROKER_PROTOCOL=SSL \
       -v ${KAFKA_SSL_SECRETS_DIR}:/etc/kafka/secrets \
       confluentinc/cp-kafka:|release|

   Check the logs to see the broker has booted up successfully:

   .. codewithvars:: bash

      docker logs kafka-ssl-1
      docker logs kafka-ssl-2
      docker logs kafka-ssl-3

   You should see start see bootup messages. For example, ``docker logs kafka-ssl-3 | grep started`` should show the following:

   .. codewithvars:: bash

      [2016-07-24 07:29:20,258] INFO [Kafka Server 1003], started (kafka.server.KafkaServer)
      [2016-07-24 07:29:20,258] INFO [Kafka Server 1003], started (kafka.server.KafkaServer)

   You should see the messages like the following on the broker acting as controller.

   .. codewithvars:: bash

      [2016-07-24 07:29:20,283] TRACE Controller 1001 epoch 1 received response {error_code=0} for a request sent to broker localhost:29092 (id: 1001 rack: null) (state.change.logger)
      [2016-07-24 07:29:20,283] TRACE Controller 1001 epoch 1 received response {error_code=0} for a request sent to broker localhost:29092 (id: 1001 rack: null) (state.change.logger)
      [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
      [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
      [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
      [2016-07-24 07:29:20,287] INFO [Controller-1001-to-broker-1003-send-thread], Controller 1001 connected to localhost:49092 (id: 1003 rack: null) for sending state change requests (kafka.controller.RequestSendThread)

#. Test that the broker is working as expected.

   Now that the brokers are up, you can test that they're working as expected by creating a topic.

   .. codewithvars:: bash

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:|release| \
        kafka-topics --create --topic bar --partitions 3 --replication-factor 3 --if-not-exists --zookeeper localhost:32181

   You should see the following output:

   .. codewithvars:: bash

    Created topic "bar".

   Now verify that the topic is created successfully by describing the topic.

   .. codewithvars:: bash

       docker run \
          --net=host \
          --rm \
          confluentinc/cp-kafka:|release| \
          kafka-topics --describe --topic bar --zookeeper localhost:32181

   You should see the following message in your terminal window:

   .. codewithvars:: bash

       Topic:bar   PartitionCount:3    ReplicationFactor:3 Configs:
       Topic: bar  Partition: 0    Leader: 1003    Replicas: 1003,1002,1001    Isr: 1003,1002,1001
       Topic: bar  Partition: 1    Leader: 1001    Replicas: 1001,1003,1002    Isr: 1001,1003,1002
       Topic: bar  Partition: 2    Leader: 1002    Replicas: 1002,1001,1003    Isr: 1002,1001,1003

   Next, you can try generating some data to the ``bar`` topic that was just created.

   .. codewithvars:: bash

        docker run \
          --net=host \
          --rm \
          -v ${KAFKA_SSL_SECRETS_DIR}:/etc/kafka/secrets \
          confluentinc/cp-kafka:|release| \
          bash -c "seq 42 | kafka-console-producer --broker-list localhost:29092 --topic bar -producer.config /etc/kafka/secrets/host.producer.ssl.config && echo 'Produced 42 messages.'"

   The command above will pass 42 integers using the Console Producer that is shipped with Kafka.  As a result, you should see something like this in your terminal:

   .. codewithvars:: bash

      Produced 42 messages.

   It looked like things were successfully written, but now you can try reading the messages back using the Console Consumer and make sure they're all accounted for.

   .. codewithvars:: bash

      docker run \
        --net=host \
        --rm \
        -v ${KAFKA_SSL_SECRETS_DIR}:/etc/kafka/secrets \
        confluentinc/cp-kafka:|release| \
        kafka-console-consumer --bootstrap-server localhost:29092 --topic bar --from-beginning --consumer.config /etc/kafka/secrets/host.consumer.ssl.config --max-messages 42

   You should see the following (it might take some time for this command to return data. Kafka has to create the ``__consumers_offset`` topic behind the scenes when you consume data for the first time and this may take some time):

   .. codewithvars:: bash

       1
       4
       7
       10
       13
       16
       ....
       41
       Processed a total of 42 messages

.. _clustered_quickstart_compose_ssl:

Docker Compose: Setting Up a Three Node Confluent Platform Cluster with SSL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you get started, you will first need to install `Docker <https://docs.docker.com/engine/installation/>`_ and `Docker Compose <https://docs.docker.com/compose/install/>`_.  Once you've done that, you can follow the steps below to start up the |cp| services.

#. Clone the |cp| Docker Images Github Repository.

   .. codewithvars:: bash

      git clone https://github.com/confluentinc/cp-docker-images
      cd cp-docker-images/examples/kafka-cluster-ssl

   Follow section 3 on generating SSL credentials in :ref:`docker-client-setup-3-node-ssl` to create the SSL credentials.

#. Start |zk| and Kafka using Docker Compose ``up`` command.

   .. codewithvars:: bash

       export KAFKA_SSL_SECRETS_DIR=$(pwd)/secrets
       docker-compose create
       docker-compose start

   In another terminal window, go to the same directory (kafka-cluster).  Make sure the services are up and running

   .. codewithvars:: bash

       docker-compose ps

   You should see the following:

   .. codewithvars:: bash

         Name                         Command            State   Ports
      -------------------------------------------------------------------------
      kafkaclusterssl_kafka-ssl-1_1   /etc/confluent/docker/run   Up
      kafkaclusterssl_kafka-ssl-2_1   /etc/confluent/docker/run   Up
      kafkaclusterssl_kafka-ssl-3_1   /etc/confluent/docker/run   Up
      kafkaclusterssl_zookeeper-1_1   /etc/confluent/docker/run   Up
      kafkaclusterssl_zookeeper-2_1   /etc/confluent/docker/run   Up
      kafkaclusterssl_zookeeper-3_1   /etc/confluent/docker/run   Up

   Check the |zk| logs to verify that |zk| is healthy. For example, for service zookeeper-1:

   .. codewithvars:: bash

      docker-compose logs zookeeper-1

   You should see messages like the following:

   .. codewithvars:: bash

      zookeeper-1_1  | [2016-07-25 04:58:12,901] INFO Created server with tickTime 2000 minSessionTimeout 4000 maxSessionTimeout 40000 datadir /var/lib/zookeeper/log/version-2 snapdir /var/lib/zookeeper/data/version-2 (org.apache.zookeeper.server.ZooKeeperServer)
      zookeeper-1_1  | [2016-07-25 04:58:12,902] INFO FOLLOWING - LEADER ELECTION TOOK - 235 (org.apache.zookeeper.server.quorum.Learner)

   Verify that ZK ensemble is ready

   .. codewithvars:: bash

       for i in 22181 32181 42181; do
          docker run --net=host --rm confluentinc/cp-zookeeper:|release| bash -c "echo stat | nc localhost $i | grep Mode"
       done

   You should see one ``leader`` and two ``follower`` instances:

   .. codewithvars:: bash

      Mode: follower
      Mode: leader
      Mode: follower

   Check the logs to see the broker has booted up successfully

   .. codewithvars:: bash

      docker-compose logs kafka-ssl-1
      docker-compose logs kafka-ssl-2
      docker-compose logs kafka-ssl-3

   You should see start see bootup messages. For example, ``docker-compose logs kafka-ssl-3 | grep started`` shows the following

   .. codewithvars:: bash

      kafka-ssl-3_1      | [2016-07-25 04:58:15,189] INFO [Kafka Server 3], started (kafka.server.KafkaServer)
      kafka-ssl-3_1      | [2016-07-25 04:58:15,189] INFO [Kafka Server 3], started (kafka.server.KafkaServer)

   You should see the messages like the following on the broker acting as controller.

   .. codewithvars:: bash

      (Tip: `docker-compose logs | grep controller` makes it easy to grep through logs for all services.)

      kafka-ssl-3_1  | [2016-08-24 23:38:22,762] INFO [Controller-3-to-broker-1-send-thread], Controller 3 connected to localhost:19093 (id: 1 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
      kafka-ssl-3_1  | [2016-08-24 23:38:22,763] INFO [Controller-3-to-broker-2-send-thread], Controller 3 connected to localhost:29093 (id: 2 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
      kafka-ssl-3_1  | [2016-08-24 23:38:22,763] INFO [Controller-3-to-broker-2-send-thread], Controller 3 connected to localhost:29093 (id: 2 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
      kafka-ssl-3_1  | [2016-08-24 23:38:22,763] INFO [Controller-3-to-broker-2-send-thread], Controller 3 connected to localhost:29093 (id: 2 rack: null) for sending state change requests (kafka.controller.RequestSendThread)
      kafka-ssl-3_1  | [2016-08-24 23:38:22,762] INFO [Controller-3-to-broker-1-send-thread], Controller 3 connected to localhost:19093 (id: 1 rack: null) for sending state change requests (kafka.controller.RequestSendThread)

#. Follow step 5 in the :ref:`docker-client-setup-3-node-ssl` to test that your brokers are functioning as expected.

#. To stop the cluster, first stop Kafka nodes one-by-one and then stop the |zk| cluster.

   .. codewithvars:: bash

    docker-compose stop kafka-ssl-1
    docker-compose stop kafka-ssl-2
    docker-compose stop kafka-ssl-3
    docker-compose down
