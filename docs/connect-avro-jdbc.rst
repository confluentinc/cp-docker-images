Now, lets extend this example to use Avro as the data format and use a JDBC Source to read from a MySQL database. For this example, make sure that the Schema registry is running.

1. Setup

  1. Kafka Connect stores config, status and offsets of the connectors in Kafka topics. We will create these topics now.

   ::

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        kafka-topics --create --topic quickstart-avro-offsets --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

   ::

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        kafka-topics --create --topic quickstart-avro-config --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

   ::

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        kafka-topics --create --topic quickstart-avro-status --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181

  2. Next we will create a topic for storing data for our quickstart.

    ::

      docker run \
        --net=host \
        --rm \
        confluentinc/cp-kafka:3.0.0 \
        kafka-topics --create --topic quickstart-avro-data --partitions 1 --replication-factor 1 --if-not-exists --zookeeper localhost:32181


  3. Verify that the topics are created.

    ::

      docker run \
         --net=host \
         --rm \
         confluentinc/cp-kafka:3.0.0 \
         kafka-topics --describe --zookeeper localhost:32181


  4. Download the MySQL JDBC driver and copy it to the ``jars`` folder (You will need to SSH into the VM to run these commands if you are running Docker Machine. You might have to run the command as root).

   ::

     mkdir -p /tmp/quickstart/jars

     curl -k -SL "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.39.tar.gz" | tar -xzf - -C /tmp/quickstart/jars --strip-components=1 mysql-connector-java-5.1.39/mysql-connector-java-5.1.39-bin.jar


2. Start a connect worker with Avro support.

  ::

      docker run -d \
        --name=kafka-connect-avro \
        --net=host \
        -e CONNECT_BOOTSTRAP_SERVERS=localhost:29092 \
        -e CONNECT_REST_PORT=28083 \
        -e CONNECT_GROUP_ID="quickstart-avro" \
        -e CONNECT_CONFIG_STORAGE_TOPIC="quickstart-avro-config" \
        -e CONNECT_OFFSET_STORAGE_TOPIC="quickstart-avro-offsets" \
        -e CONNECT_STATUS_STORAGE_TOPIC="quickstart-avro-status" \
        -e CONNECT_KEY_CONVERTER="io.confluent.connect.avro.AvroConverter" \
        -e CONNECT_VALUE_CONVERTER="io.confluent.connect.avro.AvroConverter" \
        -e CONNECT_KEY_CONVERTER_SCHEMA_REGISTRY_URL="http://localhost:8081" \
        -e CONNECT_VALUE_CONVERTER_SCHEMA_REGISTRY_URL="http://localhost:8081" \
        -e CONNECT_INTERNAL_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_INTERNAL_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
        -e CONNECT_REST_ADVERTISED_HOST_NAME="localhost" \
        -e CONNECT_LOG4J_ROOT_LOGLEVEL=DEBUG \
        -v /tmp/quickstart/file:/tmp/quickstart \
        -v /tmp/quickstart/jars:/etc/kafka-connect/jars \
        confluentinc/cp-kafka-connect:latest

3. Make sure that the connect worker is healthy.

  ::

    docker logs kafka-connect-avro | grep started

  You should see the following

  ::

    [2016-08-25 19:18:38,517] INFO Kafka Connect started (org.apache.kafka.connect.runtime.Connect)
    [2016-08-25 19:18:38,557] INFO Herder started (org.apache.kafka.connect.runtime.distributed.DistributedHerder)

4. Launch a MYSQL database

  1. Launch database container
  ::

    docker run -d \
      --name=quickstart-mysql \
      --net=host \
      -e MYSQL_ROOT_PASSWORD=confluent \
      -e MYSQL_USER=confluent \
      -e MYSQL_PASSWORD=confluent \
      -e MYSQL_DATABASE=connect_test \
      mysql

  2. Create databases and tables.
    Exec into the docker container to create the databases
    ::
      docker exec -it quickstart-mysql bash

    On the bash prompt, create a MySQL shell

    ::

      mysql -u confluent -pconfluent

    Execute the following SQL statements

    ::

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

    Exit the container shell by typing ``exit``.

  3. We will now create our JDBC Source connector using the Connect REST API. (Make sure you have curl installed.)

    Set the CONNECT_HOSTNAME.If you are running this on Docker Machine, then the hostname will be ``docker-machine ip <your docker machine name>``
    ::

      export CONNECT_HOST=localhost

    Create the JDBC Source connector.
    ::

      curl -X POST \
        -H "Content-Type: application/json" \
        --data '{ "name": "quickstart-jdbc-source-foo", "config": { "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector", "tasks.max": 1, "connection.url": "jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent", "mode": "incrementing", "incrementing.column.name": "id", "timestamp.column.name": "modified", "topic.prefix": "quickstart-jdbc-foo", "poll.interval.ms": 1000 } }' \
        http://$CONNECT_HOST:28082/connectors

    The output of this command should be
    ::

      {"name":"quickstart-jdbc-source","config":{"connector.class":"io.confluent.connect.jdbc.JdbcSourceConnector","tasks.max":"1","connection.url":"jdbc:mysql://127.0.0.1:3306/connect_test?user=root&password=confluent","mode":"incrementing","incrementing.column.name":"id","timestamp.column.name":"modified","topic.prefix":"quickstart-jdbc-","poll.interval.ms":"1000","name":"quickstart-jdbc-source"},"tasks":[]}

    Check the status of the connector using curl as follows:

    ::

      curl -s -X GET http://$CONNECT_HOST:28083/connectors/quickstart-jdbc-source/status

    You should see

    ::

      {"name":"quickstart-jdbc-source","connector":{"state":"RUNNING","worker_id":"localhost:28083"},"tasks":[{"state":"RUNNING","id":0,"worker_id":"localhost:28083"}]}

    The JDBC sink create intermediate topics for storing data. We should see a ``quickstart-jdbc-test`` topic.

    ::

      docker run \
         --net=host \
         --rm \
         confluentinc/cp-kafka:3.0.0 \
         kafka-topics --describe --zookeeper localhost:32181


    Now we will read from the ``quickstart-jdbc-test`` topic to check if the connector works.

    ::

      docker run \
       --net=host \
       --rm \
       confluentinc/cp-schema-registry:3.0.0 \
       kafka-avro-console-consumer --bootstrap-server localhost:29092 --topic quickstart-jdbc-test --new-consumer --from-beginning --max-messages 10

    You should see the following:

    ::

      {"id":1,"name":{"string":"alice"},"email":{"string":"alice@abc.com"},"department":{"string":"engineering"},"modified":1472153437000}
      {"id":2,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1472153437000}
      ....
      {"id":10,"name":{"string":"bob"},"email":{"string":"bob@abc.com"},"department":{"string":"sales"},"modified":1472153439000}
      Processed a total of 10 messages

  5. We will now launch a File Sink to read from this topic and write to an output file.

    ::

      curl -X POST -H "Content-Type: application/json" \
        --data '{"name": "quickstart-avro-file-sink", "config": {"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector", "tasks.max":"1", "topics":"quickstart-jdbc-test", "file": "/tmp/quickstart/jdbc-output.txt"}}' \
        http://$CONNECT_HOST:28083/connectors

    You should see the following in the output.
    ::

      {"name":"quickstart-avro-file-sink","config":{"connector.class":"org.apache.kafka.connect.file.FileStreamSinkConnector","tasks.max":"1","topics":"quickstart-jdbc-test","file":"/tmp/quickstart/jdbc-output.txt","name":"quickstart-avro-file-sink"},"tasks":[]}

    Check the status of the connector.

    ::

      curl -s -X GET http://$CONNECT_HOST:28083/connectors/quickstart-avro-file-sink/status

    You should see

    ::

      {"name":"quickstart-avro-file-sink","connector":{"state":"RUNNING","worker_id":"localhost:28083"},"tasks":[{"state":"RUNNING","id":0,"worker_id":"localhost:28083"}]}

    Now check the file to see if the data is present. You will need to SSH into the VM if you are running Docker Machine.

    ::

      cat /tmp/quickstart/file/jdbc-output.txt | wc -l

    You should see ``10`` as the output.

    Because of https://issues.apache.org/jira/browse/KAFKA-4070, you will not see the actual data in the file.
