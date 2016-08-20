3 node Kafka cluster
--------------------

Using Docker client
~~~~~~~~~~~~~~~~~~~

1. Run a 3-node Zookeeper ensemble

   ::

       docker run -d \
           --net=host \
           --name=zk-1 \
           -e ZOOKEEPER_SERVER_ID=1 \
           -e ZOOKEEPER_CLIENT_PORT=22181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           -e ZOOKEEPER_INIT_LIMIT=5 \
           -e ZOOKEEPER_SYNC_LIMIT=2 \
           -e ZOOKEEPER_SERVERS="localhost:22888:23888;localhost:32888:33888;localhost:42888:43888" \
           confluentinc/cp-zookeeper:3.0.0

       docker run -d \
           --net=host \
           --name=zk-2 \
           -e ZOOKEEPER_SERVER_ID=2 \
           -e ZOOKEEPER_CLIENT_PORT=32181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           -e ZOOKEEPER_INIT_LIMIT=5 \
           -e ZOOKEEPER_SYNC_LIMIT=2 \
           -e ZOOKEEPER_SERVERS="localhost:22888:23888;localhost:32888:33888;localhost:42888:43888" \
           confluentinc/cp-zookeeper:3.0.0

       docker run -d \
           --net=host \
           --name=zk-3 \
           -e ZOOKEEPER_SERVER_ID=3 \
           -e ZOOKEEPER_CLIENT_PORT=42181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           -e ZOOKEEPER_INIT_LIMIT=5 \
           -e ZOOKEEPER_SYNC_LIMIT=2 \
           -e ZOOKEEPER_SERVERS="localhost:22888:23888;localhost:32888:33888;localhost:42888:43888" \
           confluentinc/cp-zookeeper:3.0.0

   Check the logs to see the broker has booted up successfully

   ::

       docker logs zk-1

   You should see messages like this at the end of the log output

   ::

       [2016-07-24 07:17:50,960] INFO Created server with tickTime 2000 minSessionTimeout 4000 maxSessionTimeout 40000 datadir /var/lib/zookeeper/log/version-2 snapdir /var/lib/zookeeper/data/version-2 (org.apache.zookeeper.server.ZooKeeperServer)
       [2016-07-24 07:17:50,961] INFO FOLLOWING - LEADER ELECTION TOOK - 21823 (org.apache.zookeeper.server.quorum.Learner)
       [2016-07-24 07:17:50,983] INFO Getting a diff from the leader 0x0 (org.apache.zookeeper.server.quorum.Learner)
       [2016-07-24 07:17:50,986] INFO Snapshotting: 0x0 to /var/lib/zookeeper/data/version-2/snapshot.0 (org.apache.zookeeper.server.persistence.FileTxnSnapLog)
       [2016-07-24 07:17:52,803] INFO Received connection request /127.0.0.1:50056 (org.apache.zookeeper.server.quorum.QuorumCnxManager)
       [2016-07-24 07:17:52,806] INFO Notification: 1 (message format version), 3 (n.leader), 0x0 (n.zxid), 0x1 (n.round), LOOKING (n.state), 3 (n.sid), 0x0 (n.peerEpoch) FOLLOWING (my state) (org.apache.zookeeper.server.quorum.FastLeaderElection)

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

2. Run a 3 node Kafka cluster

   ::

       docker run -d \
           --net=host \
           --name=kafka-1 \
           -e KAFKA_ZOOKEEPER_CONNECT=localhost:22181,localhost:32181,localhost:42181 \
           -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
           confluentinc/cp-kafka:3.0.0

       docker run -d \
           --net=host \
           --name=kafka-2 \
           -e KAFKA_ZOOKEEPER_CONNECT=localhost:22181,localhost:32181,localhost:42181 \
           -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:39092 \
           confluentinc/cp-kafka:3.0.0

       docker run -d \
           --net=host \
           --name=kafka-3 \
           -e KAFKA_ZOOKEEPER_CONNECT=localhost:22181,localhost:32181,localhost:42181 \
           -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:49092 \
           confluentinc/cp-kafka:3.0.0

   Check the logs to see the broker has booted up successfully

   ::

       docker logs kafka-1
       docker logs kafka-2
       docker logs kafka-3

   You should see start see bootup messages. For example,
   ``docker logs kafka-3 | grep started`` shows the following

   ::

       [2016-07-24 07:29:20,258] INFO [Kafka Server 1003], started (kafka.server.KafkaServer)
       [2016-07-24 07:29:20,258] INFO [Kafka Server 1003], started (kafka.server.KafkaServer)

   You should see the messages like the following on the broker acting
   as controller.

   ::

       [2016-07-24 07:29:20,283] TRACE Controller 1001 epoch 1 received response {error_code=0} for a request sent to broker localhost:29092 (id: 1001 rack: null) (state.change.logger)
       [2016-07-24 07:29:20,283] TRACE Controller 1001 epoch 1 received response {error_code=0} for a request sent to broker localhost:29092 (id: 1001 rack: null) (state.change.logger)
       [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
       [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
       [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
       [2016-07-24 07:29:20,287] INFO [Controller-1001-to-broker-1003-send-thread], Controller 1001 connected to localhost:49092 (id: 1003 rack: null) for sending state change requests (kafka.controller.RequestSendThread)

3. Test that the broker is working fine

   i. Create a topic

   ::

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        kafka-topics --create --topic bar --partitions 3 --replication-factor 3 --if-not-exists --zookeeper localhost:32181

   You should see

   ::

       Created topic "bar".

   ii. Verify that the topic is created successfully

   ::

       docker run \
          --net=host \
          --rm \
          confluentinc/cp-kafka:3.0.0 \
          kafka-topics --describe --topic bar --zookeeper localhost:32181

   You should see

   ::

       Topic:bar   PartitionCount:3    ReplicationFactor:3 Configs:
       Topic: bar  Partition: 0    Leader: 1003    Replicas: 1003,1002,1001    Isr: 1003,1002,1001
       Topic: bar  Partition: 1    Leader: 1001    Replicas: 1001,1003,1002    Isr: 1001,1003,1002
       Topic: bar  Partition: 2    Leader: 1002    Replicas: 1002,1001,1003    Isr: 1002,1001,1003

   iii. Generate data

   ::

        docker run \
          --net=host \
          --rm confluentinc/cp-kafka:3.0.0 \
          bash -c "seq 42 | kafka-console-producer --broker-list localhost:29092 --topic bar && echo 'Produced 42 messages.'"

   You should see

   ::

       Produced 42 messages.

   iv. Read back the message using the Console consumer

   ::

       docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        kafka-console-consumer --bootstrap-server localhost:29092 --topic bar --new-consumer --from-beginning --max-messages 42

   You should see

   ::

       1
       4
       7
       10
       13
       16
       ....
       41
       Processed a total of 42 messages
