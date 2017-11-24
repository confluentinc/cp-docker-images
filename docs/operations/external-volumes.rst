.. _external_volumes :

Mounting External Volumes
-------------------------

When working with Docker, you may sometimes need to persist data in the event of a container going down or share data across containers.  In order to do so, you can use `Docker Volumes <https://docs.docker.com/engine/tutorials/dockervolumes/>`_.  In the case of Confluent Platform, we'll need to use external volumes for several main use cases:

1. Data Storage: Kafka and Zookeeper will need externally mounted volumes to persist data in the event that a container stops running or is restarted. 
2. Security: When security is configured, the secrets are stored on the the host and made available to the containers using mapped volumes.
3. Configuring Kafka Connect with External Jars: Kafka connect can be configured to use third-party jars by storing them on a volume on the host.


  .. note::

    In the event that you need to add support for additional use cases for external volumes, please refer to our guide on `extending the images <../development.html#extending-the-docker-images>`_.

Data Volumes for Kafka & Zookeeper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Kafka uses volumes for log data and Zookeeper uses volumes for transaction logs. It is recommended to seperate volumes (on the host) for these services. You will also need to ensure that the host directory has read/write permissions for the Docker container user (which is root by default unless you assign a user using Docker run command).

Below is an example of how to use Kafka and Zookeeper with mounted volumes. We also show how to configure volumes if you are running Docker container as non root user. In this example, we run the container as user 12345.

On the Docker host (e.g. Virtualbox VM), create the directories:

.. sourcecode:: bash

  # Create dirs for Kafka / ZK data
  mkdir -p /vol1/zk-data
  mkdir -p /vol2/zk-txn-logs
  mkdir -p /vol3/kafka-data

  # Make sure user 12345 has r/w permissions
  chown -R 12345 /vol1/zk-data
  chown -R 12345 /vol2/zk-txn-logs
  chown -R 12345 /vol3/kafka-data

Then start the containers:

.. sourcecode:: bash

  # Run ZK with user 12345 and volumes mapped to host volumes
  docker run -d \
    --name=zk-vols \
    --net=host \
    --user=12345 \
    -e ZOOKEEPER_TICK_TIME=2000 \
    -e ZOOKEEPER_CLIENT_PORT=32181 \
    -v /vol1/zk-data:/var/lib/zookeeper/data \
    -v /vol2/zk-txn-logs:/var/lib/zookeeper/log \
    confluentinc/cp-zookeeper:3.1.1

  docker run -d \
    --name=kafka-vols \
    --net=host \
    --user=12345 \
    -e KAFKA_BROKER_ID=1 \
    -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
    -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:39092 \
    -v /vol3/kafka-data:/var/lib/kafka/data \
    confluentinc/cp-kafka:3.1.1

The data volumes are mounted using the ``-v`` flag.  

Security: Data Volumes for Configuring Secrets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When security is enabled, the secrets are made available to the containers using volumes.  For example, if the host has the secrets (credentials, keytab, certificates, kerberos config, JAAS config) in ``/vol007/kafka-node-1-secrets``, we can configure Kafka as follows to use the secrets:

.. sourcecode:: bash
  
  docker run -d \
    --name=kafka-sasl-ssl-1 \
    --net=host \
    -e KAFKA_BROKER_ID=1 \
    -e KAFKA_ZOOKEEPER_CONNECT=localhost:22181,localhost:32181,localhost:42181/saslssl \
    -e KAFKA_ADVERTISED_LISTENERS=SASL_SSL://localhost:39094 \
    -e KAFKA_SSL_KEYSTORE_FILENAME=kafka.broker3.keystore.jks \
    -e KAFKA_SSL_KEYSTORE_CREDENTIALS=broker3_keystore_creds \
    -e KAFKA_SSL_KEY_CREDENTIALS=broker3_sslkey_creds \
    -e KAFKA_SSL_TRUSTSTORE_FILENAME=kafka.broker3.truststore.jks \
    -e KAFKA_SSL_TRUSTSTORE_CREDENTIALS=broker3_truststore_creds \
    -e KAFKA_SECURITY_INTER_BROKER_PROTOCOL=SASL_SSL \
    -e KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL=GSSAPI \
    -e KAFKA_SASL_ENABLED_MECHANISMS=GSSAPI \
    -e KAFKA_SASL_KERBEROS_SERVICE_NAME=kafka \
    -e KAFKA_OPTS=-Djava.security.auth.login.config=/etc/kafka/secrets/host_broker3_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/host_krb.conf \
    -v /vol007/kafka-node-1-secrets:/etc/kafka/secrets \
    confluentinc/cp-kafka:latest

In the example above, we specify the location of the data volumes by setting ``-v /vol007/kafka-node-1-secrets:/etc/kafka/secrets``.  We then specify how they are to be used by setting:

.. sourcecode:: bash

  -e KAFKA_OPTS=-Djava.security.auth.login.config=/etc/kafka/secrets/host_broker3_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/host_krb.conf

Configuring Connect with External jars
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Kafka connect can be configured to use third-party jars by storing them on a volume on the host and mapping the volume to ``/etc/kafka-connect/jars`` on the container.

At the host (e.g. Virtualbox VM), download the MySQL driver:

.. sourcecode:: bash  

  # Create a dir for jars and download the mysql jdbc driver into the directories
  mkdir -p /vol42/kafka-connect/jars

  # get the driver and store the jar in the dir
  curl -k -SL "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.39.tar.gz" | tar -xzf - -C /vol42/kafka-connect/jars --strip-components=1 mysql-connector-java-5.1.39/mysql-connector-java-5.1.39-bin.jar

Then start Kafka connect mounting the download directory as ``/etc/kafka-connect/jars``:

.. sourcecode:: bash  

  docker run -d \
    --name=connect-host-json \
    --net=host \
    -e CONNECT_BOOTSTRAP_SERVERS=localhost:39092 \
    -e CONNECT_REST_PORT=28082 \
    -e CONNECT_GROUP_ID="default" \
    -e CONNECT_CONFIG_STORAGE_TOPIC="default.config" \
    -e CONNECT_OFFSET_STORAGE_TOPIC="default.offsets" \
    -e CONNECT_STATUS_STORAGE_TOPIC="default.status" \
    -e CONNECT_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
    -e CONNECT_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
    -e CONNECT_INTERNAL_KEY_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
    -e CONNECT_INTERNAL_VALUE_CONVERTER="org.apache.kafka.connect.json.JsonConverter" \
    -e CONNECT_REST_ADVERTISED_HOST_NAME="localhost" \
    -v /vol42/kafka-connect/jars:/etc/kafka-connect/jars \
    confluentinc/cp-kafka-connect:latest
