.. _quickstart :

Quickstart
==========

In this section, we provide a simple guide for running a Kafka cluster along with all of the other Confluent Platform components.  By the end of this quickstart, you will have successfully installed and run a simple deployment including each component with Docker.  

In order to keep things simple, this quickstart guide is limited to a single node Kafka cluster.  For more advanced tutorials, you can refer to the following guides:

* Securing Your Cluster on Docker
* Running in a Clustered Environment 

It is also worth noting that we will be configuring Kafka and Zookeeper to store data locally in the Docker containers.  However, you can also refer to our `bla bla bla <addlink.com>`_ for an example of how to add mounted volumes to the host machine to persist data in the event that the container stops running.  This is important when running a system like Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages.  

Installing & Running Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this tutorial, we'll run docker using the Docker client.  If you are interested in information on using Docker Compose to run the images, `we have docs for that too <addlink>`_.

To get started, you'll need to first `install Docker and get it running <https://docs.docker.com/engine/installation/>`_.  The CP Docker Images require Docker version 1.11 or greater.  

Getting Started with Docker Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're running on Windows or Mac OS X, you'll need to use `Docker Machine <https://docs.docker.com/machine/install-machine/>`_ to start the Docker host.  Docker runs natively on Linux, so the Docker host will be your local machine if you go that route.  If you are running on Mac or Windows, be sure to allocate at least 4 GB of ram to the Docker Machine.

Now that we have all of the Docker dependencies installed, we can begin starting up Confluent Platform.

  .. note::

    In the following steps we'll be running each Docker container in detached mode.  However, we'll also demonstrate how access the logs for a running container.  If you prefer to run the containers in the foreground, you can do so by replacing the ``-d`` flags with ``--it``. 

1. Start Zookeeper.  You'll need to keep this service running throughout, so if you will be running things in the foreground, you'll need to have it in a dedicated terminal window.  

  .. sourcecode:: bash

    docker run -d \
        --net=host \
        --name=zookeeper \
        -e ZOOKEEPER_CLIENT_PORT=32181 \
        -e ZOOKEEPER_TICK_TIME=2000 \
        confluentinc/cp-zookeeper:3.0.0

  In this command, we tell Docker to run the ``confluentinc/cp-zookeeper:3.0.0`` container named ``zookeeper``.  We also specify that we want to use host networking and pass in the two required parameters for running Zookeeper: ``ZOOKEEPER_CLIENT_PORT`` and ``ZOOKEEPER_TICK_TIME``.  For a full list of the available configuration options and more details on passing environment variables into Docker containers, `go to this link that is yet to be created <addlink.com>`_.

  Now that we've attempted to start Zookeeper, we'll check the logs to see the server has booted up successfully by running the following command:

  .. sourcecode:: bash

    docker logs zookeeper

  With this command, we're referencing the container name we want to see the logs for.  To list all containers (running or failed), you can always run ``docker ps -a``.  This is especially useful when running in detached mode.

  When you output the logs for Zookeeper, you should see the following message at the end of the log output:

  ::

    [2016-07-24 05:15:35,453] INFO binding to port 0.0.0.0/0.0.0.0:32181 (org.apache.zookeeper.server.NIOServerCnxnFactory)

2. Start Kafka.  

  .. sourcecode:: bash

      docker run -d \
          --net=host \
          --name=kafka \
          -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
          -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
          confluentinc/cp-kafka:3.0.0

  .. note::

    You'll notice that we set the ``KAFKA_ADVERTISED_LISTENERS`` variable to ``localhost:29092``.  This will make Kafka accessible from outside the container by advertising it's location on the Docker host. 

  Let's check the logs to see the broker has booted up successfully:

  .. sourcecode:: bash

    docker logs kafka

  You should see the following at the end of the log output:

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

3. Take it for a test drive.  Test that the broker is functioning as expected by creating a topic and producing data to it:

  First, we'll create a topic.  We'll name it ``foo`` and keep things simple by just giving it one partition and only one replica.  You'll likely want to increase both if you're running in a more high-stakes environment in which you are concerned about data loss.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.0.0 \
      kafka-topics --create --topic foo --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

  You should see the following output in your terminal window:

  ::

    Created topic "foo".

  Before moving on, verify that the topic was created successfully:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.0.0 \
      kafka-topics --describe --topic foo --zookeeper localhost:32181

  You should see the following output in your terminal window:

  ::

    Topic:foo   PartitionCount:1    ReplicationFactor:1 Configs:
    Topic: foo  Partition: 0    Leader: 1001    Replicas: 1001  Isr: 1001

  Next, we'll try generating some data to our new topic:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.0.0 \
      bash -c "seq 42 | kafka-console-producer --broker-list localhost:29092 --topic foo && echo 'Produced 42 messages.'"

  This command will use the built-in Kafka Console Producer to produce 42 simple messages to the topic. Upon running it, you should see the following:

  ::

    Produced 42 messages.

  To complete the story, let's read back the message using the built-in Console consumer:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.0.0 \
      kafka-console-consumer --bootstrap-server localhost:29092 --topic foo --new-consumer --from-beginning --max-messages 42

  If everything is working as expected, each of the original messages we produced should be written back out:

  ::

    1
    ....
    42
    Processed a total of 42 messages

5. Now we have all Kafka and Zookeeper up and running, we can start trying out some of the other components included in Confluent Platform. We'll start by using the Schema Registry to create a new schema and send some Avro data to a Kafka topic. Although you would normally do this from one of your applications, we'll use a utility provided with Schema Registry to send the data without having to write any code. 

  First, let's fire up the Schema Registry container:

  .. sourcecode:: bash

    docker run -d \
      --net=host \
      --name=schema-registry \
      -e SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL=localhost:32181 \
      -e SCHEMA_REGISTRY_HOST_NAME=localhost \
      -e SCHEMA_REGISTRY_LISTENERS=http://localhost:8081 \
      confluentinc/cp-schema-registry:3.0.0 

  As we did before, we can check that it started correctly by viewing the logs.

  .. sourcecode:: bash

    docker logs schema-registry

  Next, let's ``exec`` into the Schema Registry container, where we'll be using the ``kafka-avro-console-producer`` utility is located.

  .. sourcecode:: bash

    docker run -it --net=host --rm confluentinc/cp-schema-registry:3.0.0 bash

  Direct the utility at the local Kafka cluster, tell it to write to the topic ``foo``, read each line of input as an Avro message, validate the schema against the Schema Registry at the specified URL, and finally indicate the format of the data.

  .. sourcecode:: bash

    usr/bin/kafka-avro-console-producer \
      --broker-list localhost:29092 --topic bar \
      --property value.schema='{"type":"record","name":"myrecord","fields":[{"name":"f1","type":"string"}]}'

  Once started, the process will wait for you to enter messages, one per line, and will send them immediately when you hit the ``Enter`` key. Try entering a few messages:

  ::

    {"f1": "value1"}
    {"f1": "value2"}
    {"f1": "value3"}

  .. note::

    If you hit ``Enter`` with an empty line, it will be interpreted as a null value and cause an error. You can simply start the console producer again to continue sending messages.

  When you're done, use ``Ctrl+C`` to shut down the process.  You can also type ``exit`` to leave the container.  Now that we wrote avro data to Kafka, we should check that the data was actually produced as expected by trying to consume it.  Although the Schema Registry also ships with a built-in console consumer utility, we'll instead demonstrate how to read it from outside the container on our local machine via the REST Proxy.  The REST Proxy depends on the Schema Registry when producing/consuming avro data, so let's leave the container running as we head to the next step.

6. Consume data via the REST Proxy.

   First, start up the REST Proxy:

  .. sourcecode:: bash

    docker run -d \
      --net=host \
      --name=kafka-rest \
      -e KAFKA_REST_ZOOKEEPER_CONNECT=localhost:32181 \
      -e KAFKA_REST_LISTENERS=http://localhost:8082 \
      -e KAFKA_REST_SCHEMA_REGISTRY_URL=http://localhost:8081 \
      confluentinc/cp-kafka-rest:3.0.0

  For the next two steps, we're going to use CURL commands to talk to the REST Proxy.  You should be able to run these from your local machine, but that will require you to know the IP address of your Docker image.  For the sake of simplicity, we'll just exec into the Schema Registry again to run them from the host network by pointing to http://localhost:8082.  

  .. sourcecode:: bash

    docker run -it --net=host --rm confluentinc/cp-schema-registry:3.0.0 bash

  Next, we'll need to create a consumer for Avro data, starting at the beginning of the log for our topic, ``bar``.  As you can see in the startup command, we passed the ``KAFKA_REST_LISTENERS`` to ensure that the REST Proxy will be listening on port ``8082``.

  .. sourcecode:: bash

    curl -X POST -H "Content-Type: application/vnd.kafka.v1+json" \
      --data '{"name": "my_consumer_instance", "format": "avro", "auto.offset.reset": "smallest"}' \
      http://localhost:8082/consumers/my_avro_consumer

  You should see the following in your terminal window:

  .. sourcecode:: bash

    {"instance_id":"my_consumer_instance","base_uri":"http://localhost:8082/consumers/my_avro_consumer/instances/my_consumer_instance"}

  Now we'll consume some data from a topic.  It will be decoded, translated to JSON, and included in the response. The schema used for deserialization is fetched automatically from the Schema Registry, which we told the REST Proxy how to find by setting the ``KAFKA_REST_SCHEMA_REGISTRY_URL`` variable on startup.

  .. sourcecode:: bash

    curl -X GET -H "Accept: application/vnd.kafka.avro.v1+json" \
      http://localhost:8082/consumers/my_avro_consumer/instances/my_consumer_instance/topics/bar
  
  You should see the following output:

  .. sourcecode:: bash  
  
    [{"key":null,"value":{"f1":"value1"},"partition":0,"offset":0},{"key":null,"value":{"f1":"value2"},"partition":0,"offset":1},{"key":null,"value":{"f1":"value3"},"partition":0,"offset":2}]

7. Once you're done, cleaning up is simple.  You can simply run ``docker rm -f $(docker ps -a -q)`` to delete all the containers we created in the steps above.  Because we allowed Kafka and Zookeeper to store data on their respective containers, there are no additional volumes to clean up.  If you also want to remove the Docker machine you used, you can do so using ``docker-machine rm <machine-name>>``.


Getting Started with Docker Compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you get started, you will first need to install `Docker <https://docs.docker.com/engine/installation/>`_ and `Docker Compose <https://docs.docker.com/compose/install/>`_.  Once you've done that, you can follow the steps below to start up the Confluent Platform services 

1. Clone the CP Docker Images Github Repository.

  .. sourcecode:: bash

    git clone https://github.com/confluentinc/cp-docker-images

  We have provided an example Docker Compose file that will start up Zookeeper and Kafka.  Navigate to ``cp-docker-images/examples/kafka-single-node``, where it is located:

  .. sourcecode:: bash       
    cd cp-docker-images/examples/kafka-single-node

2. Start Zookeeper and Kafka using Docker Compose ``start`` and ``run`` commands.

   .. sourcecode:: bash

       docker-compose start
       docker-compose run

   Before we move on, let's make sure the services are up and running:

   .. sourcecode:: bash

       docker-compose ps

   You should see the following:

   .. sourcecode:: bash

                  Name                        Command            State   Ports
       -----------------------------------------------------------------------
       kafkasinglenode_kafka_1       /etc/confluent/docker/run   Up
       kafkasinglenode_zookeeper_1   /etc/confluent/docker/run   Up

   Now check the Zookeeper logs to verify that Zookeeper is healthy.

   .. sourcecode:: bash

       docker-compose log zookeeper | grep -i binding

   You should see the following in your terminal window:

   .. sourcecode:: bash

       zookeeper_1  | [2016-07-25 03:26:04,018] INFO binding to port 0.0.0.0/0.0.0.0:32181 (org.apache.zookeeper.server.NIOServerCnxnFactory)

   Next, check the Kafka logs to verify that broker is healthy.

   .. sourcecode:: bash

       docker-compose log kafka | grep -i started

   You should see message a message that looks like the following:

   .. sourcecode:: bash

       kafka_1      | [2016-07-25 03:26:06,007] INFO [Kafka Server 1], started (kafka.server.KafkaServer)

3. Follow section 3 in "CP Quickstart with Docker Client" guide above to test the broker.
