.. _cpdocker_intro:

Docker Images for Confluent Platform
================================

Docker images for the Confluent Platform are currently available on `DockerHub <https://hub.docker.com/u/confluentinc/>`_.


Quickstart
-------------------------

In this section, we provide a quickstart guide for running a single node Kafka cluster along with all of the other Confluent Platform components.  By the end of this quickstart, you will have successfully installed and run a simple deployment including each component with Docker.  For more advanced tutorials, you can refer to the following guides:

- TODO: add sumit's other quickstarts here

Prerequisites
~~~~~~~~~~~~~~~~~~~

- Docker: https://docs.docker.com/engine/installation/
- Docker Machine: https://docs.docker.com/machine/install-machine/
- Kafka: 0.10.0.0-cp1

Using Docker Client
~~~~~~~~~~~~~~~~~~~

1. Run Zookeeper

   ::

       docker run -d \
           --net=host \
           --name=zookeeper \
           -e ZOOKEEPER_CLIENT_PORT=32181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           confluentinc/cp-zookeeper:3.0.0

   Check the logs to see the server has booted up successfully:

   ::

       docker logs zookeeper

   You should see the following message at the end of the log output:

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

   Check the logs to see the broker has booted up successfully:

   ::

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

3. Test that the broker is functioning as expected by creating a topic and producing data to it:

  i. Create a topic

    ::

      docker run \
        --net=host \
        --rm confluentinc/cp-kafka:3.0.0 \
        kafka-topics --create --topic foo --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

    You should see

    ::

      Created topic "foo".

  ii. Verify that the topic is created successfully

    ::

      docker run \
        --net=host \
        --rm confluentinc/cp-kafka:3.0.0 \
        kafka-topics --describe --topic foo --zookeeper localhost:32181

    You should see:

    ::

      Topic:foo   PartitionCount:1    ReplicationFactor:1 Configs:
      Topic: foo  Partition: 0    Leader: 1001    Replicas: 1001  Isr: 1001

  iii. Generate data.

    ::

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        bash -c "seq 42 | kafka-console-producer --broker-list localhost:29092 --topic foo && echo 'Produced 42 messages.'"

    You should see:

    ::

      Produced 42 messages.

  iv. Read back the message using the Console consumer

    ::

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        kafka-console-consumer --bootstrap-server localhost:29092 --topic foo --new-consumer --from-beginning --max-messages 42

    You should see:

    ::

      1
      ....
      42
      Processed a total of 42 messages

4. Start the Schema Registry.

  ::

    docker run -d \
      --net=host \
      --name=schema-registry \
      -e SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL=localhost:32181 \
      -e SCHEMA_REGISTRY_HOST_NAME=localhost \
      confluentinc/cp-schema-registry:3.0.0

4. Start the REST Proxy.

  ::

    docker run -d \
      --net=host \
      --name=kafka-rest \
      -e KAFKA_REST_ZOOKEEPER_CONNECT=localhost:32181 \
      confluentinc/cp-kafka-rest:3.0.0

5. Start Kafka Connect.

  .. sourcecode:: bash

    TODO: SUMIT!  DO THIS!!!

6. Start Confluent Control Center

  .. sourcecode:: bash

    TODO: SUMIT!  DO THIS!!!

7. Now we have all the services up and running, we can send some Avro data to a Kafka topic. Although you would normally do this from one of your applications, we'll use a utility provided with Kafka to send the data without having to write any code.

  To start, let's ``exec`` into the Schema Registry container, where we'll be using the ``kafka-avro-console-producer`` utility is located.

  ::

    docker run -it --net=host --rm confluentinc/cp-schema-registry:3.0.0 bash

  Now let's direct the utility at our local Kafka cluster, tell it to write to the topic ``foo``, read each line of input as an Avro message, validate the schema against the Schema Registry at the specified URL, and finally indicate the format of the data.

  ::

    usr/bin/kafka-avro-console-producer \
      --broker-list localhost:9092 --topic bar \
      --property value.schema='{"type":"record","name":"myrecord","fields":[{"name":"f1","type":"string"}]}'

  Once started, the process will wait for you to enter messages, one per line, and will send them immediately when you hit the ``Enter`` key. Try entering a few messages:

  ::

    {"f1": "value1"}
    {"f1": "value2"}
    {"f1": "value3"}

  When you're done, use ``Ctrl+C`` to shut down the process.

  .. note::

    If you hit ``Enter`` with an empty line, it will be interpreted as a null value and cause an error. You can simply start the console producer again to continue sending messages.

  Now we can check that the data was produced by using Kafka’s console consumer process to read data from the topic.  We point it at the same ``bar`` topic, our ZooKeeper instance, tell it to decode each message using Avro using the same Schema Registry URL to look up schemas, and finally tell it to start from the beginning of the topic (by default the consumer only reads messages published after it starts).  You can now type ``exit`` to leave the container.  Instead of running the consumer utility from within the container, we'll try passing the command through.  

  ::

    docker run \
      --net=host \
      --rm confluentinc/cp-schema-registry:3.0.0 \
      bash -c "usr/bin/kafka-avro-console-consumer --topic bar --zookeeper localhost:32181 --from-beginning"

  You should see all the messages you created in the previous step written to the console in the same format.

  ::

    {"f1": "value1"}
    {"f1": "value2"}
    {"f1": "value3"}

  The consumer does not exit after reading all the messages so it can listen for and process new messages as they are published. Try keeping the consumer running and repeating the previous step – you will see messages delivered to the consumer immediately after you hit ``Enter`` for each message in the producer.

  When you’re done, shut down the consumer with Ctrl+C.


License
-------

The Confluent Platform Docker Images are available as open source software under the Apache License v2.0 license.  For more information on the licenses for each of the individual Confluent Platform components packaged in the images, please refer to the `respective Confluent Platform documentation for each component <http://docs.confluent.io/3.0.0/platform.html>`_.  Source code for these Docker images is available at https://github.com/confluentinc/cp-docker-images.
