.. _replicator :

Replicator Tutorial
-------------------

In this section, we provide a tutorial for running Replicator which replicates data from two source Kafka clusters to a destination Kafka cluster.  By the end of this tutorial, you will have successfully run Replicator and replicated data for two topics from different source clusters to a destination cluster.  Furthermore, you will have also set up a Kafka Connect cluster because Replicator is built on Connect.

It is worth noting that we will be configuring Kafka and Zookeeper to store data locally in the Docker containers.  For deployments that require persistent data (e.g. production deployments), you should use mounted volumes for persisting data in the event that a container stops running or is restarted.  This is important when running a system like Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages. Refer to our `documentation on Docker external volumes <operations/external-volumes.html>`_ for an example of how to add mounted volumes to the host machine.

Installing & Running Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this tutorial, we'll run Docker using Docker Compose.

To get started, you will first need to install `Docker <https://docs.docker.com/engine/installation/>`_ and `Docker Compose <https://docs.docker.com/compose/install/>`_.  The CP Docker Images require Docker version 1.11 or greater.

Once you've done that, you can follow the steps below to start up the Confluent Platform services.

1. Create and configure the Docker Machine (OS X only).

  .. sourcecode:: bash

    docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent

  Next, configure your terminal window to attach it to your new Docker Machine:

  .. sourcecode:: bash

    eval $(docker-machine env confluent)

2. Clone the CP Docker Images Github Repository.

  .. sourcecode:: bash

    git clone https://github.com/confluentinc/cp-docker-images

  We have provided an example Docker Compose file that will start up 2 source Kafka clusters, one destination Kafka cluster and a Kafka Connect cluster.  Navigate to ``cp-docker-images/examples/enterprise-replicator``, where it is located:

  .. sourcecode:: bash
    cd cp-docker-images/examples/enterprise-replicator


3. Start the Kafka and Kafka Connect clusters using Docker Compose ``create`` and ``start`` commands.

  .. sourcecode:: bash

    docker-compose create

  You should see the following

  .. sourcecode:: bash

    Creating enterprisereplicator_kafka-1-src-b_1
    Creating enterprisereplicator_kafka-1-src-a_1
    Creating enterprisereplicator_kafka-2-dest_1
    Creating enterprisereplicator_zookeeper-src-b_1
    Creating enterprisereplicator_zookeeper-src-a_1
    Creating enterprisereplicator_connect-host-1_1
    Creating enterprisereplicator_kafka-2-src-a_1
    Creating enterprisereplicator_kafka-2-src-b_1
    Creating enterprisereplicator_kafka-1-dest_1
    Creating enterprisereplicator_zookeeper-dest_1
    Creating enterprisereplicator_connect-host-2_1

  Start all the services

  .. sourcecode:: bash

    docker-compose start

  You should see the following

  .. sourcecode:: bash

    Starting kafka-1-src-b ... done
    Starting kafka-1-src-a ... done
    Starting kafka-2-dest ... done
    Starting zookeeper-src-b ... done
    Starting zookeeper-src-a ... done
    Starting connect-host-1 ... done
    Starting kafka-2-src-a ... done
    Starting kafka-2-src-b ... done
    Starting kafka-1-dest ... done
    Starting zookeeper-dest ... done
    Starting connect-host-2 ... done

  Before we move on, let's make sure the services are up and running:

  .. sourcecode:: bash

    docker-compose ps

  You should see the following:

  .. sourcecode:: bash

      Name                             Command            State   Ports
    ----------------------------------------------------------------------------------
    enterprisereplicator_connect-host-1_1    /etc/confluent/docker/run   Up
    enterprisereplicator_connect-host-2_1    /etc/confluent/docker/run   Up
    enterprisereplicator_kafka-1-dest_1      /etc/confluent/docker/run   Up
    enterprisereplicator_kafka-1-src-a_1     /etc/confluent/docker/run   Up
    enterprisereplicator_kafka-1-src-b_1     /etc/confluent/docker/run   Up
    enterprisereplicator_kafka-2-dest_1      /etc/confluent/docker/run   Up
    enterprisereplicator_kafka-2-src-a_1     /etc/confluent/docker/run   Up
    enterprisereplicator_kafka-2-src-b_1     /etc/confluent/docker/run   Up
    enterprisereplicator_zookeeper-dest_1    /etc/confluent/docker/run   Up
    enterprisereplicator_zookeeper-src-a_1   /etc/confluent/docker/run   Up
    enterprisereplicator_zookeeper-src-b_1   /etc/confluent/docker/run   Up

  Now check the Zookeeper logs for destination cluster to verify that Zookeeper is healthy.

  .. sourcecode:: bash

    docker-compose logs zookeeper-dest | grep -i binding

  You should see the following in your terminal window:

  .. sourcecode:: bash

    zookeeper-dest_1   | [2016-10-20 17:31:40,784] INFO binding to port 0.0.0.0/0.0.0.0:42181 (org.apache.zookeeper.server.NIOServerCnxnFactory)

  Next, check the Kafka logs for the destination cluster to verify that it is healthy:

  .. sourcecode:: bash

    docker-compose logs kafka-1-dest | grep -i started

  You should see message a message that looks like the following:

  .. sourcecode:: bash

    kafka-1-dest_1     | [2016-10-20 17:31:45,364] INFO [Socket Server on Broker 1002], Started 1 acceptor threads (kafka.network.SocketServer)
    kafka-1-dest_1     | [2016-10-20 17:31:45,792] INFO [Kafka Server 1002], started (kafka.server.KafkaServer)
    ....

  Similarly verify that the ``source-a`` and ``source-b`` Kafka clusters are ready by running the following commands and verifying the output as described in the steps above.

  .. sourcecode:: bash

    docker-compose logs zookeeper-src-a | grep -i binding
    docker-compose logs zookeeper-src-b | grep -i binding
    docker-compose logs kafka-1-src-a | grep -i started
    docker-compose logs kafka-1-src-b | grep -i started

  Now, let's check to make sure that the Connect worker is up by running the following command to search the logs:

  .. sourcecode:: bash

    docker-compose logs connect-host-1 | grep started

  You should see the following

  .. sourcecode:: bash

    connect-host-1_1   | [2016-10-20 17:31:48,942] INFO Kafka Connect started (org.apache.kafka.connect.runtime.Connect)
    connect-host-1_1   | [2016-10-20 17:31:50,403] INFO Worker started (org.apache.kafka.connect.runtime.Worker)
    connect-host-1_1   | [2016-10-20 17:31:50,988] INFO Herder started (org.apache.kafka.connect.runtime.distributed.DistributedHerder)


4. We will now create our first Kafka Connect Replicator connector for replicating topic "foo" from source cluster ``source-a``.

  First, we'll create a topic.  We'll name it ``foo``.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-topics --create --topic foo --partitions 3 --replication-factor 2 --if-not-exists --zookeeper localhost:22181

  You should see the following output in your terminal window:

  .. sourcecode:: bash

    Created topic "foo".

  Before moving on, verify that the topic was created successfully:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-topics --describe --topic foo --zookeeper localhost:22181

  You should see the following output in your terminal window:

  .. sourcecode:: bash

    Topic:foo      	PartitionCount:3       	ReplicationFactor:2    	Configs:
    Topic: foo     	Partition: 0   	Leader: 1002   	Replicas: 1002,1001    	Isr: 1002,1001
    Topic: foo     	Partition: 1   	Leader: 1001   	Replicas: 1001,1002    	Isr: 1001,1002
    Topic: foo     	Partition: 2   	Leader: 1002   	Replicas: 1002,1001    	Isr: 1002,1001

5. Next, we'll try generating some data to our new topic:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      bash -c "seq 1000 | kafka-console-producer --request-required-acks 1 --broker-list localhost:9092 --topic foo && echo 'Produced 1000 messages.'"

  This command will use the built-in Kafka Console Producer to produce 100 simple messages to the topic. Upon running it, you should see the following:

  .. sourcecode:: bash

    Produced 1000 messages.

6. Now create the connector using the Kafka Connect REST API.  First, let's exec into the Connect container.

  .. sourcecode:: bash

    docker-compose exec connect-host-1 bash

  You should see a bash prompt now. We will call this the ``docker exec`` command prompt:

  .. sourcecode:: bash

    root@confluent:/#

  The next step is to create the Replicator connector. Run the following command on the ``docker exec`` command prompt.

  .. sourcecode:: bash

    curl -X POST \
         -H "Content-Type: application/json" \
         --data '{
            "name": "replicator-src-a-foo",
            "config": {
              "connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector",
              "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
              "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
              "src.zookeeper.connect": "localhost:22181",
              "src.kafka.bootstrap.servers": "localhost:9092",
              "dest.zookeeper.connect": "localhost:42181",
              "topic.whitelist": "foo",
              "topic.rename.format": "${topic}.replica"}}'  \
         http://localhost:28082/connectors

  Upon running the command, you should see the following output in your ``docker exec`` command prompt:

  .. sourcecode:: bash

    {"name":"replicator-src-a-foo","config":{"connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector","key.converter":"io.confluent.connect.replicator.util.ByteArrayConverter","value.converter":"io.confluent.connect.replicator.util.ByteArrayConverter","src.zookeeper.connect":"localhost:22181","src.kafka.bootstrap.servers":"localhost:9092","dest.zookeeper.connect":"localhost:42181","topic.whitelist":"foo","topic.rename.format":"${topic}.replica","name":"replicator-src-a-foo"},"tasks":[]}

  Before moving on, let's check the status of the connector using curl on the ``docker exec`` command prompt.

  .. sourcecode:: bash

    curl -X GET http://localhost:28082/connectors/replicator-src-a-foo/status

  You should see the following output including the ``state`` of the connector as ``RUNNING``:

  .. sourcecode:: bash

    {"name":"replicator-src-a-foo","connector":{"state":"RUNNING","worker_id":"localhost:38082"},"tasks":[{"state":"RUNNING","id":0,"worker_id":"localhost:28082"}]}

  Exit the ``docker exec`` command prompt by typing ``exit`` on the prompt.

  .. sourcecode:: bash

    exit

7. Now that the connector is up and running, it should replicate data from ``foo`` topic on ``source-a`` cluster to ``foo.replica`` topic on the ``dest`` cluster.

  Let's try reading a sample of 1000 records from the ``foo.replica`` topic to check if the connector is replicating data to the destination Kafka cluster, as expected. Run the following command on your terminal (Make sure you have exited the ``docker exec`` command prompt):

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-console-consumer --bootstrap-server localhost:9072 --topic foo.replica --new-consumer --from-beginning --max-messages 1000

  If everything is working as expected, each of the original messages we produced should be written back out:

  .. sourcecode:: bash

    1
    ....
    1000
    Processed a total of 1000 messages

  We will now verify that the destination topic is created with correct replication factor and partition count.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-topics --describe --topic foo.replica --zookeeper localhost:42181

  You should see that the topic ``foo.replica`` is created with 3 partitions and 2 replicas, same as the original topic ``foo``.

  .. sourcecode:: bash

    Topic:foo.replica      	PartitionCount:3       	ReplicationFactor:2    	Configs:message.timestamp.type=CreateTime
    Topic: foo.replica     	Partition: 0   	Leader: 1002   	Replicas: 1002,1001    	Isr: 1002,1001
    Topic: foo.replica     	Partition: 1   	Leader: 1001   	Replicas: 1001,1002    	Isr: 1001,1002
    Topic: foo.replica     	Partition: 2   	Leader: 1002   	Replicas: 1002,1001    	Isr: 1002,1001

8. Now, we will replicate another topic from a different source cluster.

  First, lets create a new topic on the cluster ``source-b`` and add some data to it. Run the following commands to create and verify the topic. You should see output similar to steps 4 and 5 above:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-topics --create --topic bar --partitions 3 --replication-factor 2 --if-not-exists --zookeeper localhost:32181

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-topics --describe --topic bar --zookeeper localhost:32181

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      bash -c "seq 1000 | kafka-console-producer --request-required-acks 1 --broker-list localhost:9082 --topic bar && echo 'Produced 1000 messages.'"

  Now lets ``exec`` into the Kafka Connect container and run the replicator connector. Enter the following commands on your terminal. You should see output similar to step 6 above.

  Run the following to into the container to get ``docker exec`` command prompt.

  .. sourcecode:: bash

    docker-compose exec connect-host-1 bash

  Run the following command on the ``docker exec`` command prompt.

  .. sourcecode:: bash

    curl -X POST \
         -H "Content-Type: application/json" \
         --data '{
            "name": "replicator-src-b-bar",
            "config": {
              "connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector",
              "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
              "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
              "src.zookeeper.connect": "localhost:32181",
              "src.kafka.bootstrap.servers": "localhost:9082",
              "dest.zookeeper.connect": "localhost:42181",
              "topic.whitelist": "bar",
              "topic.rename.format": "${topic}.replica"}}'  \
         http://localhost:28082/connectors

  .. sourcecode:: bash

    curl -X GET http://localhost:28082/connectors/replicator-src-b-bar/status


  Exit the ``docker exec`` command prompt by typing ``exit`` on the prompt.

  .. sourcecode:: bash

    exit

9. Now that the second replicator connector is up and running, it should replicate data from ``bar`` topic on ``source-b`` cluster to ``bar.replica`` topic on the ``dest`` cluster.

  Let's try reading a data from ``bar.replica`` topic to check if the connector is replicating data properly followed by describing the topic to verify that the destination topic was created properly. You should see output similar to step 7 above. as expected.

  Run the following commands on your terminal (Make sure you have exited the ``docker exec`` command prompt):

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-console-consumer --bootstrap-server localhost:9072 --topic bar.replica --new-consumer --from-beginning --max-messages 1000

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.5.0-SNAPSHOT \
      kafka-topics --describe --topic bar.replica --zookeeper localhost:42181

10. Feel free to experiment with the replicator connector on your own now. When you are done, use the following commands to shutdown all the components.

  .. sourcecode:: bash

    docker-compose stop

  If you want to remove all the containers, run:

  .. sourcecode:: bash

    docker-compose rm
