Single node Kafka
-----------------

Using Docker client
~~~~~~~~~~~~~~~~~~~

0. Install docker
1. Run Zookeeper

   ::

       docker run -d \
           --net=host \
           --name=zookeeper \
           -e ZOOKEEPER_CLIENT_PORT=32181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           confluentinc/cp-zookeeper:3.0.0

   Check the logs to see the server has booted up successfully

   ::

       docker logs zookeeper

   You should see this at the end of the log output

   ::

       [2016-07-24 05:15:35,453] INFO binding to port 0.0.0.0/0.0.0.0:32181 (org.apache.zookeeper.server.NIOServerCnxnFactory)

2. Run Kafka

   ::

       docker run -d \
           --net=host \
           --name=kafka \
           -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
           -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
           confluentinc/cp-kafka:3.0.0

   Check the logs to see the broker has booted up successfully

   ::

       docker logs kafka

   You should see this at the end of the log output

   ::

       ....
       [2016-07-15 23:31:00,295] INFO [Kafka Server 1], started (kafka.server.KafkaServer)
       [2016-07-15 23:31:00,295] INFO [Kafka Server 1], started (kafka.server.KafkaServer)
       ...
       ...
       [2016-07-15 23:31:00,349] INFO [Controller 1]: New broker startup callback for 1 (kafka.controller.KafkaController)
       [2016-07-15 23:31:00,349] INFO [Controller 1]: New broker startup callback for 1 (kafka.controller.KafkaController)
       [2016-07-15 23:31:00,350] INFO [Controller-1-to-broker-1-send-thread], Starting  (kafka.controller.RequestSendThread)
       ...

3. Test that the broker is working fine

   i. Create a topic

   ::

      docker run --net=host --rm confluentinc/cp-kafka:3.0.0 kafka-topics --create --topic foo --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

   You should see

   ::

       Created topic "foo".

   ii. Verify that the topic is created successfully

   ::

       docker run --net=host --rm confluentinc/cp-kafka:3.0.0 kafka-topics --describe --topic foo --zookeeper localhost:32181

   You should see

   ::

       Topic:foo   PartitionCount:1    ReplicationFactor:1 Configs:
           Topic: foo  Partition: 0    Leader: 1001    Replicas: 1001  Isr: 1001

   iii. Generate data

   ::

        docker run --net=host --rm confluentinc/cp-kafka:3.0.0 bash -c "seq 42 \
          | kafka-console-producer --broker-list localhost:29092 --topic foo && echo 'Produced 42 messages.'"

   You should see

   ::

       Produced 42 messages.

   iv. Read back the message using the Console consumer

   ::

       docker run --net=host --rm confluentinc/cp-kafka:3.0.0 kafka-console-consumer --bootstrap-server localhost:29092 --topic foo --new-consumer --from-beginning --max-messages 42

   You should see

   ::

       1
       ....
       42
       Processed a total of 42 messages
