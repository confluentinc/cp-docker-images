.. _quickstart :

Quickstart
==========

In this section, we provide a simple guide for running a Kafka cluster along with all of the other Confluent Platform components.  By the end of this quickstart, you will have successfully installed and run a simple deployment including each component with Docker.

In order to keep things simple, this quickstart guide is limited to a single node Confluent Platform cluster.  For more advanced tutorials, you can refer to the following guides:

* Securing Your Cluster on Docker
* Running in a Clustered Environment

It is also worth noting that we will be configuring Kafka and Zookeeper to store data locally in the Docker containers.  However, you can also refer to our `bla bla bla <addlink.com>`_ for an example of how to add mounted volumes to the host machine to persist data in the event that the container stops running.  This is important when running a system like Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages.

Installing & Running Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this tutorial, we'll run Docker using the Docker client.  If you are interested in information on using Docker Compose to run the images, `we have docs for that too <addlink>`_.

To get started, you'll need to first `install Docker and get it running <https://docs.docker.com/engine/installation/>`_.  The CP Docker Images require Docker version 1.11 or greater.

Getting Started with Docker Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're running on Windows or Mac OS X, you'll need to use `Docker Machine <https://docs.docker.com/machine/install-machine/>`_ to start the Docker host.  Docker runs natively on Linux, so the Docker host will be your local machine if you go that route.  If you are running on Mac or Windows, be sure to allocate at least 4 GB of ram to the Docker Machine.

Now that we have all of the Docker dependencies installed, we can create a Docker machine and begin starting up Confluent Platform.

  .. note::

    In the following steps we'll be running each Docker container in detached mode.  However, we'll also demonstrate how access the logs for a running container.  If you prefer to run the containers in the foreground, you can do so by replacing the ``-d`` flags with ``--it``.

1. Create and configure  the Docker Machine.

  .. sourcecode:: bash

    docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent

  Next, configure your terminal window to attach it to your new Docker Machine:

  .. sourcecode:: bash

    eval $(docker-machine env confluent)

2. Start Zookeeper.  You'll need to keep this service running throughout, so if you will be running things in the foreground, you'll need to have it in a dedicated terminal window.

  .. sourcecode:: bash

    docker run -d \
        --net=host \
        --name=zookeeper \
        -e ZOOKEEPER_CLIENT_PORT=32181 \
        -e ZOOKEEPER_TICK_TIME=2000 \
        confluentinc/cp-zookeeper:3.0.1

  In this command, we tell Docker to run the ``confluentinc/cp-zookeeper:3.0.1`` container named ``zookeeper``.  We also specify that we want to use host networking and pass in the two required parameters for running Zookeeper: ``ZOOKEEPER_CLIENT_PORT`` and ``ZOOKEEPER_TICK_TIME``.  For a full list of the available configuration options and more details on passing environment variables into Docker containers, `go to this link that is yet to be created <addlink.com>`_.

  Now that we've attempted to start Zookeeper, we'll check the logs to see the server has booted up successfully by running the following command:

  .. sourcecode:: bash

    docker logs zookeeper

  With this command, we're referencing the container name we want to see the logs for.  To list all containers (running or failed), you can always run ``docker ps -a``.  This is especially useful when running in detached mode.

  When you output the logs for Zookeeper, you should see the following message at the end of the log output:

  ::

    [2016-07-24 05:15:35,453] INFO binding to port 0.0.0.0/0.0.0.0:32181 (org.apache.zookeeper.server.NIOServerCnxnFactory)

3. Start Kafka.

  .. sourcecode:: bash

      docker run -d \
          --net=host \
          --name=kafka \
          -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
          -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
          confluentinc/cp-kafka:3.0.1

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

4. Take it for a test drive.  Test that the broker is functioning as expected by creating a topic and producing data to it:

  First, we'll create a topic.  We'll name it ``foo`` and keep things simple by just giving it one partition and only one replica.  You'll likely want to increase both if you're running in a more high-stakes environment in which you are concerned about data loss.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.0.1 \
      kafka-topics --create --topic foo --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

  You should see the following output in your terminal window:

  ::

    Created topic "foo".

  Before moving on, verify that the topic was created successfully:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.0.1 \
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
      confluentinc/cp-kafka:3.0.1 \
      bash -c "seq 42 | kafka-console-producer --broker-list localhost:29092 --topic foo && echo 'Produced 42 messages.'"

  This command will use the built-in Kafka Console Producer to produce 42 simple messages to the topic. Upon running it, you should see the following:

  ::

    Produced 42 messages.

  To complete the story, let's read back the message using the built-in Console consumer:

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.0.1 \
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
      confluentinc/cp-schema-registry:3.0.1

  As we did before, we can check that it started correctly by viewing the logs.

  .. sourcecode:: bash

    docker logs schema-registry

  For the next two steps, we're going to use CURL commands to talk to the Schema Registry. For the sake of simplicity, we'll run a new Schema Registry container on the same host, where we'll be using the ``kafka-avro-console-producer`` utility.

  .. sourcecode:: bash

    docker run -it --net=host --rm confluentinc/cp-schema-registry:3.0.1 bash

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
      confluentinc/cp-kafka-rest:3.0.1

  For the next two steps, we're going to use CURL commands to talk to the REST Proxy. For the sake of simplicity, we'll run a new Schema Registry container on the same host to run them from the host network by pointing to http://localhost:8082.

  .. sourcecode:: bash

    docker run -it --net=host --rm confluentinc/cp-schema-registry:3.0.1 bash

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

7. We will walk you through an end-to-end data transfer pipeline using Kafka Connect. We'll start by reading data from a file and write it back to a file.  We will then extend the pipeline to show how to use connect to read from a database.  This example is meant to be simple for the sake of this introductory tutorial.  If you'd like a more in-depth example, please refer to `our tutorial on using a JDBC connector with avro data <connect_quickstart_avro_jdbc.html>`_.

  First, let's start up Kafka Connect.  Connect stores config, status, and offsets of the connectors in Kafka topics. We will create these topics now.  We already have Kafka up and running from the steps above.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.0.1 \
      kafka-topics --create --topic quickstart-offsets --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.0.1 \
      kafka-topics --create --topic quickstart-config --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:3.0.1 \
      kafka-topics --create --topic quickstart-status --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

  .. note::

    It is possible to allow connect to auto-create these topics by enabling the autocreation setting.  However, we recommend doing it manually, as these topics are important for connect to function and you'll likely want to control the settings.

  Next, we'll create a topic for storing data that we're going to be sending to Kafka for this tutorial.

    .. sourcecode:: bash

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.1 \
        kafka-topics --create --topic quickstart-data --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181


  Now you should verify that the topics are created before moving on:

  .. sourcecode:: bash

    docker run \
       --net=host \
       --rm \
       confluentinc/cp-kafka:3.0.1 \
       kafka-topics --describe --zookeeper localhost:32181

  For this example, we'll create File Connectors and directories for storing the input and output files. If you are running Docker Machine then you will need to SSH into the VM to run these commands by running ``docker-machine ssh <your machine name>``. You may also need to run the command as root.

  First, let's create the directory where we'll store the input and output data files:

  .. sourcecode:: bash

    mkdir -p /tmp/quickstart/file

  Next, start a Connect worker in distributed mode:

  .. sourcecode:: bash

      docker run -d \
        --name=kafka-connect \
        --net=host \
        -e CONNECT_BOOTSTRAP_SERVERS=localhost:29092 \
        -e CONNECT_REST_PORT=28082 \
        -e CONNECT_GROUP_ID="quickstart" \
        -e CONNECT_CONFIG_STORAGE_TOPIC="quickstart-config" \
        -e CONNECT_OFFSET_STORAGE_TOPIC="quickstart-offsets" \
        -e CONNECT_STATUS_STORAGE_TOPIC="quickstart-status" \
        -e CONNECT_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_INTERNAL_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_INTERNAL_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_REST_ADVERTISED_HOST_NAME="localhost" \
        -e CONNECT_LOG4J_ROOT_LOGLEVEL=DEBUG \
        -v /tmp/quickstart/file:/tmp/quickstart \
        confluentinc/cp-kafka-connect:3.0.1

  As you can see in the command above, we tell Connect to refer to the three topics we create in the first step of this Connect tutorial. Let's check to make sure that the Connect worker is up by running the following command to search the logs:

  .. sourcecode:: bash

    docker logs kafka-connect | grep started

  You should see the following

  .. sourcecode:: bash

    [2016-08-25 18:25:19,665] INFO Herder started (org.apache.kafka.connect.runtime.distributed.DistributedHerder)
    [2016-08-25 18:25:19,676] INFO Kafka Connect started (org.apache.kafka.connect.runtime.Connect)

  We will now create our first connector for reading a file from disk.  To do this, let's start by creating a file with some data. Again, if you are running Docker Machine then you will need to SSH into the VM to run these commands by running ``docker-machine ssh <your machine name>``. (You may also need to run the command as root).

  .. sourcecode:: bash

    seq 1000 > /tmp/quickstart/file/input.txt

  Now create the connector using the Kafka Connect REST API. (Note: Make sure you have curl installed!)

  Set the ``CONNECT_HOST`` environment variable.  If you are running this on Docker Machine, then the hostname will need to be ``docker-machine ip <your docker machine name>``. If you are running on a cloud provider like AWS, you will either need to have port ``28082`` open or you can SSH into the VM and run the following command:

  .. sourcecode:: bash

    export CONNECT_HOST=localhost

  The next step is to create the File Source connector.

  .. sourcecode:: bash

    curl -X POST \
      -H "Content-Type: application/json" \
      --data '{"name": "quickstart-file-source", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSourceConnector", "tasks.max":"1", "topic":"quickstart-data", "file": "/tmp/quickstart/input.txt"}}' \
      http://$CONNECT_HOST:28082/connectors

  Upon running the command, you should see the following output in your terminal window:

  .. sourcecode:: bash

    {"name":"quickstart-file-source","config":{"connector.class":"org.apache.kafka.connect.file.FileStreamSourceConnector","tasks.max":"1","topic":"quickstart-data","file":"/tmp/quickstart/input.txt","name":"quickstart-file-source"},"tasks":[]}


  Before moving on, let's check the status of the connector using curl as shown below:

  .. sourcecode:: bash

    curl -X GET http://$CONNECT_HOST:28082/connectors/quickstart-file-source/status

  You should see the following output including the ``state`` of the connector as ``RUNNING``:

  .. sourcecode:: bash

    {"name":"quickstart-file-source","connector":{"state":"RUNNING","worker_id":"localhost:28082"},"tasks":[{"state":"RUNNING","id":0,"worker_id":"localhost:28082"}]}

  Now that the connector is up and running, let's try reading a sample of 10 records from the ``quickstart-data`` topic to check if the connector is uploading data to Kafka, as expected.

  .. sourcecode:: bash

    docker run \
     --net=host \
     --rm \
     confluentinc/cp-kafka:3.0.1 \
     kafka-console-consumer --bootstrap-server localhost:29092 --topic quickstart-data --new-consumer --from-beginning --max-messages 10

  You should see the following:

  .. sourcecode:: bash

    {"schema":{"type":"string","optional":false},"payload":"1"}
    {"schema":{"type":"string","optional":false},"payload":"2"}
    {"schema":{"type":"string","optional":false},"payload":"3"}
    {"schema":{"type":"string","optional":false},"payload":"4"}
    {"schema":{"type":"string","optional":false},"payload":"5"}
    {"schema":{"type":"string","optional":false},"payload":"6"}
    {"schema":{"type":"string","optional":false},"payload":"7"}
    {"schema":{"type":"string","optional":false},"payload":"8"}
    {"schema":{"type":"string","optional":false},"payload":"9"}
    {"schema":{"type":"string","optional":false},"payload":"10"}
    Processed a total of 10 messages

  Success!  We now have a functioning source connector!  Now let's bring balance to the universe by launching a File Sink to read from this topic and write to an output file.  You can do so using the following command:

  .. sourcecode:: bash

    curl -X POST -H "Content-Type: application/json" \
        --data '{"name": "quickstart-file-sink", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"quickstart-data", "file": "/tmp/quickstart/output.txt"}}' \
        http://$CONNECT_HOST:28082/connectors

  You should see the output below in your terminal window, confirming that the ``quickstart-file-sink`` connector has been created and will write to ``/tmp/quickstart/output.txt``:

  .. sourcecode:: bash

    {"name":"quickstart-file-sink","config":{"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector","tasks.max":"1","topics":"quickstart-data","file":"/tmp/quickstart/output.txt","name":"quickstart-file-sink"},"tasks":[]}

  As we did before, let's check the status of the connector:

  .. sourcecode:: bash

    curl -s -X GET http://$CONNECT_HOST:28082/connectors/quickstart-file-sink/status

  You should see the following message in your terminal window:

  .. sourcecode:: bash

    {"name":"quickstart-file-sink","connector":{"state":"RUNNING","worker_id":"localhost:28082"},"tasks":[{"state":"RUNNING","id":0,"worker_id":"localhost:28082"}]}

  Finally, let's check the file to see if the data is present. Once again, you will need to SSH into the VM if you are running Docker Machine.

  .. sourcecode:: bash

    cat /tmp/quickstart/file/output.txt

  If everything worked as planned, you should see all of the data we originally wrote to the input file:

  .. sourcecode:: bash

    1
    ...
    1000

8. We will walk you through how to run Confluent Control Center with a couple of examples: one with console producers and consumers and another using the Kafka Connect source and sink we've previously created.

  First, let's launch Confluent Control Center. We already have ZooKeeper and Kafka up and running from the steps above.  Let's make a directory on the host for Control Center data. If you are running Docker Machine then you will need to SSH into the VM to run these commands by running ``docker-machine ssh <your machine name>`` and run the command as root.

  .. sourcecode:: bash

    mkdir -p /tmp/control-center/data

  Now we start Control Center and bind it's data directory to the directory we just created and bind it's HTTP interface to port 9021.

  .. sourcecode:: bash

    docker run -d \
      --name=control-center \
      --net=host \
      --ulimit nofile=16384:16384 \
      -p 9021:9021 \
      -v /tmp/control-center/data:/var/lib/confluent-control-center \
      -e CONTROL_CENTER_ZOOKEEPER_CONNECT=localhost:32181 \
      -e CONTROL_CENTER_BOOTSTRAP_SERVERS=localhost:29092 \
      -e CONTROL_CENTER_REPLICATION_FACTOR=1 \
      -e CONTROL_CENTER_MONITORING_INTERCEPTOR_TOPIC_PARTITIONS=1 \
      -e CONTROL_CENTER_INTERNAL_TOPICS_PARTITIONS=1 \
      -e CONTROL_CENTER_STREAMS_NUM_STREAM_THREADS=2 \
      -e CONTROL_CENTER_CONNECT_CLUSTER=http://localhost:28082 \
      confluentinc/cp-control-center:3.0.1

  Control Center will create the topics is needs in Kafka.  Check that it started correctly by searching it's logs with the following command:

  .. sourcecode:: bash

    docker logs control-center | grep Started

  You should see the following

  .. sourcecode:: bash

    [2016-08-26 18:47:26,809] INFO Started NetworkTrafficServerConnector@26d96e5{HTTP/1.1}{0.0.0.0:9021} (org.eclipse.jetty.server.NetworkTrafficServerConnector)
    [2016-08-26 18:47:26,811] INFO Started @5211ms (org.eclipse.jetty.server.Server)

  To see the Control Center UI, navigate in a browser using HTTP to port 9021 of the docker host.  If you're using docker-machine, you can get your host IP by running ``docker-machine ip <your machine name>``.  If your docker daemon is running on a remote machine (such as an AWS EC2 instance), you'll need to open port 9021 to allow outside TCP access. In AWS, you do this by adding a "Custom TCP Rule" to the security group for port 9021 from any source IP.

  Initially, the Stream Monitoring UI will have no data.

  TODO - show screen shot

  Next, we'll run the console producer and consumer with monitoring interceptors configured and see the data in Control Center.  First we need to create a topic for testing.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm confluentinc/cp-kafka:3.0.1 \
      kafka-topics --create --topic c3-test --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

  Now use the console producer with the monitoring interceptor enabled to send data.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      -e CLASSPATH=/usr/share/java/monitoring-interceptors/monitoring-interceptors-3.0.1.jar \
      confluentinc/cp-kafka-connect:3.0.1 \
      bash -xc 'seq 10000 | kafka-console-producer --broker-list localhost:29092 --topic c3-test --producer-property interceptor.classes=io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor --producer-property acks=1 && echo "Produced 10000 messages."'

  This command will use the built-in Kafka Console Producer to produce 10000 simple messages to the topic. Upon running it, you should see the following:

  ::

    Produced 10000 messages.

  Use the console consumer with the monitoring interceptor enabled to read the data.

  .. sourcecode:: bash

    docker run \
      --net=host \
      --rm \
      -e CLASSPATH=/usr/share/java/monitoring-interceptors/monitoring-interceptors-3.0.1.jar \
      confluentinc/cp-kafka-connect:3.0.1 \
      bash -xc 'echo "interceptor.classes=io.confluent.monitoring.clients.interceptor.MonitoringConsumerInterceptor" > /tmp/consumer.props; exec kafka-console-consumer --new-consumer --bootstrap-server localhost:29092 --topic c3-test --consumer.config /tmp/consumer.props --from-beginning --max-messages=10000'

  If everything is working as expected, each of the original messages we produced should be written back out:

  ::

    1
    ....
    10000
    Processed a total of 10000 messages

  After 15 seconds have passed, you should see this activity reflected in the Control Center UI.

  TODO - show screen shot

  TODO - run the consumer again and see expected consumption change??

  Next we'll see how to monitor Kafka Connect using the monitoring interceptors.  Stop the Kafka Connect container that's already running.

  .. sourcecode:: bash

    docker stop kafka-connect; docker rm kafka-connect

  Restart Kafka Connect with the interceptors configured.

  .. sourcecode:: bash

    docker run -d \
      --name=kafka-connect \
      --net=host \
      -e CONNECT_PRODUCER_INTERCEPTOR_CLASSES=io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor \
      -e CONNECT_CONSUMER_INTERCEPTOR_CLASSES=io.confluent.monitoring.clients.interceptor.MonitoringConsumerInterceptor \
      -e CONNECT_BOOTSTRAP_SERVERS=localhost:29092 \
      -e CONNECT_REST_PORT=28082 \
      -e CONNECT_GROUP_ID="quickstart" \
      -e CONNECT_CONFIG_STORAGE_TOPIC="quickstart-config" \
      -e CONNECT_OFFSET_STORAGE_TOPIC="quickstart-offsets" \
      -e CONNECT_STATUS_STORAGE_TOPIC="quickstart-status" \
      -e CONNECT_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_INTERNAL_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_INTERNAL_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
      -e CONNECT_REST_ADVERTISED_HOST_NAME="localhost" \
      -e CONNECT_LOG4J_ROOT_LOGLEVEL=DEBUG \
      -v /tmp/quickstart/file:/tmp/quickstart \
      confluentinc/cp-kafka-connect:3.0.1

  Let's check to make sure that the Connect worker successfully restarted by running the following command to search the logs:

  .. sourcecode:: bash

    docker logs kafka-connect | grep started

  You should see the following

  .. sourcecode:: bash

    [2016-08-25 18:25:19,665] INFO Herder started (org.apache.kafka.connect.runtime.distributed.DistributedHerder)
    [2016-08-25 18:25:19,676] INFO Kafka Connect started (org.apache.kafka.connect.runtime.Connect)

  Check the Control Center UI and should see both the source and sink running in Kafka Connect.

  TODO - screen shot

  We will now add more data to the source file so that it gets loaded into Kafka and dumped back out to the output file.  If you are using docker-machine then you will need to SSH into the VM to run this commands by running ``docker-machine ssh <your machine name>`` and run the command as root.

  .. sourcecode:: bash

    seq 10000 > /tmp/quickstart/file/input.txt

  After about 15 seconds, you should start to see stream monitoring data from Kafka Connect in the Control Center UI.

  TODO - screen shot

9. Once you're done, cleaning up is simple.  You can simply run ``docker rm -f $(docker ps -a -q)`` to delete all the containers we created in the steps above.  Because we allowed Kafka and Zookeeper to store data on their respective containers, there are no additional volumes to clean up.  If you also want to remove the Docker machine you used, you can do so using ``docker-machine rm <your machine name>``.


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

3. Follow step 4 in "Getting Started with Docker Client" guide above to test the broker.
