.. _connect_quickstart_avro_jdbc:

Kafka Connect Tutorial on Docker
================================

This tutorial uses Avro as the data format and use a JDBC Source Connector to read from a MySQL database.

You must first startup up |zk|, Kafka and the Schema Registry. 

.. note::

    Schema Registry is a dependency for Connect in this tutorial because it used with the Avro serializer functionality.

It is worth noting that we will be configuring Kafka and |zk| to store data locally in the Docker containers.  For production deployments (or generally whenever you care about not losing data), you should use mounted volumes for persisting data in the event that a container stops running or is restarted.  This is important when running a system like Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages.  Refer to our :ref:`documentation on Docker external volumes <external_volumes>` for an example of how to add mounted volumes to the host machine.

.. include:: includes/docker-tutorials.rst
    :start-line: 11
    :end-line: 19

Starting Up Confluent Platform and Kafka Connect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have all of the Docker dependencies installed, we can create a Docker machine and begin starting up |cp|.

.. note::

    In the following steps we'll be running each Docker container in detached mode.  However, we'll also demonstrate how access the logs for a running container.  If you prefer to run the containers in the foreground, you can do so by replacing the ``-d`` flags with ``-it``.

#. Create and configure the Docker machine.

   .. codewithvars:: bash

    docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent

   Next, configure your terminal window to attach it to your new Docker Machine:

   .. codewithvars:: bash

    eval $(docker-machine env confluent)

#. Start up |zk|, Kafka, and Schema Registry.

   We'll walk through each of the commands for starting up these services, but you should refer to the :ref:`single-node-basic` for a more detailed walkthrough.

   Start |zk|:

   .. codewithvars:: bash

    docker run -d \
        --net=host \
        --name=zookeeper \
        -e ZOOKEEPER_CLIENT_PORT=32181 \
        -e ZOOKEEPER_TICK_TIME=2000 \
        confluentinc/cp-zookeeper:|release|

   Start Kafka:

   .. codewithvars:: bash

    docker run -d \
        --net=host \
        --name=kafka \
        -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
        -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
        -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
        confluentinc/cp-kafka:|release|

   .. note:: To make Kafka accessible from outside the container by advertising its location on the Docker host, the
             ``KAFKA_ADVERTISED_LISTENERS`` variable is set to ``localhost:29092``. The ``offsets.topic.replication.factor``
             is set to 1 at runtime, since there is only one active broker in this example.


   Start the Schema Registry:

   .. codewithvars:: bash

    docker run -d \
      --net=host \
      --name=schema-registry \
      -e SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL=localhost:32181 \
      -e SCHEMA_REGISTRY_HOST_NAME=localhost \
      -e SCHEMA_REGISTRY_LISTENERS=http://localhost:8081 \
      confluentinc/cp-schema-registry:|release|

   You can confirm that each of the services is up by checking the logs using the following command: ``docker logs <container_name>``. For example, if we run ``docker logs kafka``, we should see the following at the end of the log output:

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

#. Now let's start up Kafka Connect.  Connect stores config, status, and offsets of the connectors in Kafka topics. We will create these topics now using the Kafka broker we created above.

   .. codewithvars:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:|release| \
      kafka-topics --create --topic quickstart-avro-offsets --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

   .. codewithvars:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:|release| \
      kafka-topics --create --topic quickstart-avro-config --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

   .. codewithvars:: bash

    docker run \
      --net=host \
      --rm \
      confluentinc/cp-kafka:|release| \
      kafka-topics --create --topic quickstart-avro-status --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

   Before moving on, you can verify that the topics are created:

   .. codewithvars:: bash

    docker run \
       --net=host \
       --rm \
       confluentinc/cp-kafka:|release| \
       kafka-topics --describe --zookeeper localhost:32181


#. Download the MySQL JDBC driver and copy it to the ``jars`` folder.  If you are running Docker Machine, you will need to SSH into the VM to run these commands. You may have to run the command as root.

   First, create a folder named ``jars``:

   .. codewithvars:: bash

    mkdir -p /tmp/quickstart/jars

   Then download the JDBC driver:

   .. codewithvars:: bash

    curl -k -SL "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-8.0.11.tar.gz" | tar -xzf - -C /tmp/quickstart/jars --strip-components=1 mysql-connector-java-8.0.11/mysql-connector-java-8.0.11-bin.jar


#. Start a connect worker with Avro support.

   .. codewithvars:: bash

      docker run -d \
        --name=kafka-connect-avro \
        --net=host \
        -e CONNECT_BOOTSTRAP_SERVERS=localhost:29092 \
        -e CONNECT_REST_PORT=28083 \
        -e CONNECT_GROUP_ID="quickstart-avro" \
        -e CONNECT_CONFIG_STORAGE_TOPIC="quickstart-avro-config" \
        -e CONNECT_OFFSET_STORAGE_TOPIC="quickstart-avro-offsets" \
        -e CONNECT_STATUS_STORAGE_TOPIC="quickstart-avro-status" \
        -e CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR=1 \
        -e CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR=1 \
        -e CONNECT_STATUS_STORAGE_REPLICATION_FACTOR=1 \
        -e CONNECT_KEY_CONVERTER="io.confluent.connect.avro.AvroConverter" \
        -e CONNECT_VALUE_CONVERTER="io.confluent.connect.avro.AvroConverter" \
        -e CONNECT_KEY_CONVERTER_SCHEMA_REGISTRY_URL="http://localhost:8081" \
        -e CONNECT_VALUE_CONVERTER_SCHEMA_REGISTRY_URL="http://localhost:8081" \
        -e CONNECT_INTERNAL_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_INTERNAL_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_REST_ADVERTISED_HOST_NAME="localhost" \
        -e CONNECT_LOG4J_ROOT_LOGLEVEL=DEBUG \
        -e CONNECT_PLUGIN_PATH=/usr/share/java,/etc/kafka-connect/jars \
        -v /tmp/quickstart/file:/tmp/quickstart \
        -v /tmp/quickstart/jars:/etc/kafka-connect/jars \
        confluentinc/cp-kafka-connect:latest

#. Make sure that the connect worker is healthy.

   .. codewithvars:: bash

    docker logs kafka-connect-avro | grep started

   You should see the following output in your terminal window:

   .. codewithvars:: bash

    [2016-08-25 19:18:38,517] INFO Kafka Connect started (org.apache.kafka.connect.runtime.Connect)
    [2016-08-25 19:18:38,557] INFO Herder started (org.apache.kafka.connect.runtime.distributed.DistributedHerder)

#. Launch a MYSQL database.

   First, launch the database container

   .. codewithvars:: bash

    docker run -d \
      --name=quickstart-mysql \
      --net=host \
      -e MYSQL_ROOT_PASSWORD=confluent \
      -e MYSQL_USER=confluent \
      -e MYSQL_PASSWORD=confluent \
      -e MYSQL_DATABASE=connect_test \
      mysql

   Next, Create databases and tables.  You'll need to exec into the Docker container to create the databases.

   .. codewithvars:: bash

    docker exec -it quickstart-mysql bash

   On the bash prompt, create a MySQL shell

   .. codewithvars:: bash

    mysql -u confluent -pconfluent

   Now, execute the following SQL statements:

   .. codewithvars:: bash

      CREATE DATABASE IF NOT EXISTS connect_test;
      USE connect_test;

      DROP TABLE IF EXISTS test;


      CREATE TABLE IF NOT EXISTS test (
        id serial NOT NULL PRIMARY KEY,
        name varchar(100),
        email varchar(200),
        department varchar(200),
        modified timestamp default CURRENT_TIMESTAMP NOT NULL,
        INDEX `modified_index` (`modified`)
      );

      INSERT INTO test (name, email, department) VALUES ('alice', 'alice@abc.com', 'engineering');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      INSERT INTO test (name, email, department) VALUES ('bob', 'bob@abc.com', 'sales');
      exit;

   Finally, exit the container shell by typing ``exit``.

#. Create our JDBC Source connector using the Connect REST API. (You'll need to have curl installed)

   Set the CONNECT_HOST.  If you are running this on Docker Machine, then the hostname will be ``docker-machine ip <your docker machine name>``.

   .. codewithvars:: bash

    export CONNECT_HOST=localhost

   Create the JDBC Source connector.

   .. codewithvars:: bash

      curl -X POST \
        -H "Content-Type: application/json" \
        --data '{ "name": "quickstart-jdbc-source", "config": { "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector", "tasks.max": 1, "connection.url": "jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent", "mode": "incrementing", "incrementing.column.name": "id", "timestamp.column.name": "modified", "topic.prefix": "quickstart-jdbc-", "poll.interval.ms": 1000 } }' \
        http://$CONNECT_HOST:28083/connectors

   The output of this command should be similar to the message shown below:

   .. codewithvars:: bash

      {"name":"quickstart-jdbc-source","config":{"connector.class":"io.confluent.connect.jdbc.JdbcSourceConnector","tasks.max":"1","connection.url":"jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent","mode":"incrementing","incrementing.column.name":"id","timestamp.column.name":"modified","topic.prefix":"quickstart-jdbc-","poll.interval.ms":"1000","name":"quickstart-jdbc-source"},"tasks":[]}

   Check the status of the connector using curl as follows:

   .. codewithvars:: bash

    curl -s -X GET http://$CONNECT_HOST:28083/connectors/quickstart-jdbc-source/status

   You should see the following:

   .. codewithvars:: bash

      {"name":"quickstart-jdbc-source","connector":{"state":"RUNNING","worker_id":"localhost:28083"},"tasks":[{"state":"RUNNING","id":0,"worker_id":"localhost:28083"}]}

   The JDBC sink create intermediate topics for storing data. We should see a ``quickstart-jdbc-test`` topic.

   .. codewithvars:: bash

    docker run \
       --net=host \
       --rm \
       confluentinc/cp-kafka:|release| \
       kafka-topics --describe --zookeeper localhost:32181


   Now you will read from the ``quickstart-jdbc-test`` topic to check if the connector works.

   .. codewithvars:: bash

      docker run \
       --net=host \
       --rm \
       confluentinc/cp-schema-registry:|release| \
       kafka-avro-console-consumer --bootstrap-server localhost:29092 --topic quickstart-jdbc-test --from-beginning --max-messages 10

   You should see the following:

   .. codewithvars:: bash

      {"id":1,"name":{"string":"alice"},"email":{"string":"alice@abc.com"},"department":{"string":"engineering"},"modified":1472153437000}
      {"id":2,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1472153437000}
      ....
      {"id":10,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1472153439000}
      Processed a total of 10 messages

#. You will now launch a File Sink to read from this topic and write to an output file.

   .. codewithvars:: bash

      curl -X POST -H "Content-Type: application/json" \
        --data '{"name": "quickstart-avro-file-sink", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"quickstart-jdbc-test", "file": "/tmp/quickstart/jdbc-output.txt"}}' \
        http://$CONNECT_HOST:28083/connectors

   You should see the following in the output.

   .. codewithvars:: bash

      {"name":"quickstart-avro-file-sink","config":{"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector","tasks.max":"1","topics":"quickstart-jdbc-test","file":"/tmp/quickstart/jdbc-output.txt","name":"quickstart-avro-file-sink"},"tasks":[]}

   Check the status of the connector by running the following curl command:

   .. codewithvars:: bash

    curl -s -X GET http://$CONNECT_HOST:28083/connectors/quickstart-avro-file-sink/status

   You should get the response shown below:

   .. codewithvars:: bash

    {"name":"quickstart-avro-file-sink","connector":{"state":"RUNNING","worker_id":"localhost:28083"},"tasks":[{"state":"RUNNING","id":0,"worker_id":"localhost:28083"}]}

   Now check the file to see if the data is present. You will need to SSH into the VM if you are running Docker Machine.

   .. codewithvars:: bash

    cat /tmp/quickstart/file/jdbc-output.txt | wc -l

   You should see ``10`` as the output.

   Because of https://issues.apache.org/jira/browse/KAFKA-4070, you will not see the actual data in the file.

#. Once you're done, cleaning up is simple.  You can simply run ``docker rm -f $(docker ps -a -q)`` to delete all the containers we created in the steps above.  Because we allowed Kafka and |zk| to store data on their respective containers, there are no additional volumes to clean up.  If you also want to remove the Docker machine you used, you can do so using ``docker-machine rm <machine-name>>``.
