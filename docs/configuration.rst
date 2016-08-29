.. _config_reference :

Configuration
=============

The Confluent Platform Docker images support passing configuration variables dynamically using environment variables.  More specifically, we use the Docker ``-e`` or ``--env`` flags for setting various settings in the respective images when starting up the images.

Some configuration variables are required when starting up the Docker images.  We have outlined those variables below for each component along with an example of how to pass them.  For a full list of all available configuration options for each CP component, you should refer to the respective documentation.

	.. note::

		As you will notice, the configuration variable names have prefixed with the name of the component.  For example, the Kafka image will take variables prefixed with ``KAFKA_``.

Zookeeper
---------

The Zookeeper image uses variables prefixed with ``ZOOKEEPER_`` with the variables expressed exactly as they would appear in the ``zookeeper.properties`` file.  As an example, to set ``clientPort``, ``tickTime``, and ``syncLimit`` you'd run the command below:

	.. sourcecode:: bash

		docker run -d \
      --net=host \
      --name=zookeeper \
      -e ZOOKEEPER_CLIENT_PORT=32181 \
      -e ZOOKEEPER_TICK_TIME=2000 \
      -e ZOOKEEPER_SYNC_LIMIT=2
      confluentinc/cp-zookeeper:3.0.1

Required Settings
"""""""""""""""""

``ZOOKEEPER_CLIENT_PORT``

  This field is always required.  Tells Zookeeper where to listen for connections by clients such as Kafka.

``ZOOKEEPER_TICK_TIME``

  This field is always required.  The length of a single tick, which is the basic time unit used by ZooKeeper, as measured in milliseconds. It is used to regulate heartbeats, and timeouts. For example, the minimum session timeout will be two ticks.

``ZOOKEEPER_SYNC_LIMIT``

  Only required when running in clustered mode.  Amount of time, in ticks (see ``ZOOKEEPER_TICK_TIME``), to allow followers to sync with ZooKeeper. If followers fall too far behind a leader, they will be dropped.

``ZOOKEEPER_INIT_LIMIT``

  Only required when running in clustered mode. Amount of time, in ticks (see ``ZOOKEEPER_TICK_TIME``), to allow followers to connect and sync to a leader. Increased this value as needed, if the amount of data managed by ZooKeeper is large.

``ZOOKEEPER_SERVER_ID``

  Only required when running in clustered mode.  Sets the server ID in the ``myid`` file, which consists of a single line containing only the text of that machine's id. So ``myid`` of server 1 would contain the text "1" and nothing else. The id must be unique within the ensemble and should have a value between 1 and 255.

Kafka
-----

The Kafka image uses variables prefixed with ``KAFKA_`` with an underscore (_) separating each word instead of periods. As an example, to set ``broker.id``, ``advertised.listeners`` and ``zookeeper.connect`` you'd run the following command:

  .. sourcecode:: bash

      docker run -d \
          --net=host \
          --name=kafka \
          -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
          -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
          -e KAFKA_BROKER_ID=2 \
          confluentinc/cp-kafka:3.0.1

  .. note::

    You'll notice that we set the ``KAFKA_ADVERTISED_LISTENERS`` variable to ``localhost:29092``.  This is an important setting, as it will make Kafka accessible from outside the container by advertising it's location on the Docker host.

Required Settings
"""""""""""""""""

``KAFKA_ZOOKEEPER_CONNECT``

  Tells Kafka how to get in touch with Zookeeper.

``KAFKA_ADVERTISED_LISTENERS``

  Advertised listeners is required for starting up the Docker image because it is important to think through how other clients are going to connect to kafka.  In a Docker environment, you will need to make sure that your clients can connect to Kafka and other services.  Advertised listeners is how it gives out a host name that can be reached by the client.

Schema Registry
---------------

For the Schema Registry image, use variables prefixed with ``SCHEMA_REGISTRY_`` with an underscore (_) separating each word instead of periods. As an example, to set ``kafkastore.connection.url``, ``host.name``, ``listeners`` and ``debug`` you'd run the following:

  .. sourcecode:: bash

    docker run -d \
      --net=host \
      --name=schema-registry \
      -e SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL=localhost:32181 \
      -e SCHEMA_REGISTRY_HOST_NAME=localhost \
      -e SCHEMA_REGISTRY_LISTENERS=http://localhost:8081 \
      -e SCHEMA_REGISTRY_DEBUG=true \
      confluentinc/cp-schema-registry:3.0.1

Required Settings
"""""""""""""""""

``SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL``

  Zookeeper URL for the Kafka cluster.

``SCHEMA_REGISTRY_LISTENERS``

  Comma-separated list of listeners that listen for API requests over either HTTP or HTTPS. If a listener uses HTTPS, the appropriate SSL configuration parameters need to be set as well.

  Schema Registry identities are stored in ZooKeeper and are made up of a hostname and port. If multiple listeners are configured, the first listener's port is used for its identity.


Kafka REST Proxy
----------------

For the Kafka REST Proxy image use variables prefixed with ``KAFKA_REST_`` with an underscore (_) separating each word instead of periods. As an example, to set the ``listeners``, ``schema.registry.url`` and ``zookeeper.connect`` you'd run the following command:

  .. sourcecode:: bash

    docker run -d \
      --net=host \
      --name=kafka-rest \
      -e KAFKA_REST_ZOOKEEPER_CONNECT=localhost:32181 \
      -e KAFKA_REST_LISTENERS=http://localhost:8082 \
      -e KAFKA_REST_SCHEMA_REGISTRY_URL=http://localhost:8081 \
      confluentinc/cp-kafka-rest:3.0.1

Required Settings
"""""""""""""""""
The following settings must be passed to run the REST Proxy Docker image.

``KAFKA_REST_LISTENERS``

  Comma-separated list of listeners that listen for API requests over either HTTP or HTTPS. If a listener uses HTTPS, the appropriate SSL configuration parameters need to be set as well.

``KAFKA_REST_SCHEMA_REGISTRY_URL``

  The base URL for the schema registry that should be used by the Avro serializer.

``KAFKA_REST_ZOOKEEPER_CONNECT``

  Specifies the ZooKeeper connection string in the form hostname:port where host and port are the host and port of a ZooKeeper server. To allow connecting through other ZooKeeper nodes when that ZooKeeper machine is down you can also specify multiple hosts in the form hostname1:port1,hostname2:port2,hostname3:port3.

  The server may also have a ZooKeeper ``chroot`` path as part of it's ZooKeeper connection string which puts its data under some path in the global ZooKeeper namespace. If so the consumer should use the same chroot path in its connection string. For example to give a chroot path of /chroot/path you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

Kafka Connect
---------------

The Kafka Connect image uses variables prefixed with ``CONNECT_`` with an underscore (_) separating each word instead of periods. As an example, to set the required properties like ``bootstrap.servers``, the topic names for ``config``, ``offsets`` and ``status`` as well the ``key`` or ``value`` convertor, you'd run the following command:

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
      confluentinc/cp-kafka-connect:latest

Required Settings
"""""""""""""""""
The following settings must be passed to run the Kafka Connect Docker image.

``CONNECT_BOOTSTRAP_SERVERS``

  A unique string that identifies the Connect cluster group this worker belongs to.

``CONNECT_GROUP_ID``

  The topic to store connector and task configuration data in. This must be the same for all workers with the same ``group.id``

``CONNECT_CONFIG_STORAGE_TOPIC``

  The topic to store connector and task configuration data in. This must be the same for all workers with the same ``group.id``

``CONNECT_OFFSET_STORAGE_TOPIC``

  The topic to store offset data for connectors in. This must be the same for all workers with the same ``group.id``

``CONNECT_STATUS_STORAGE_TOPIC``

  The topic to store connector offset state in. This must be the same for all workers with the same ``group.id``

``CONNECT_KEY_CONVERTER``

  Converter class for key Connect data. This controls the format of the data that will be written to Kafka for source connectors or read from Kafka for sink connectors.

``CONNECT_VALUE_CONVERTER``

  Converter class for value Connect data. This controls the format of the data that will be written to Kafka for source connectors or read from Kafka for sink connectors.

``CONNECT_INTERNAL_KEY_CONVERTER``

  Converter class for internal key Connect data that implements the ``Converter`` interface.

``CONNECT_INTERNAL_VALUE_CONVERTER``

  Converter class for internal value Connect data that implements the ``Converter`` interface.

``CONNECT_REST_ADVERTISED_HOST_NAME``

  Advertised host name is required for starting up the Docker image because it is important to think through how other clients are going to connect to Connect.  In a Docker environment, you will need to make sure that your clients can connect to Connect and other services.  Advertised host name is how Connect gives out a host name that can be reached by the client.

Optional Settings
"""""""""""""""""
All other settings for Connect like security, monitoring interceptors, producer and consumer overrides can passed to the Docker images as environment variables. The names of these environment variables are derived by replacing ``.`` with ``_``, converting the resulting string to uppercase and prefixing it with ``CONNECT_``. For example, if you need to set ``ssl.key.password``, the environment variable name would be ``CONNECT_SSL_KEY_PASSWORD``.

The image will then convert these environment variables to corresponding Connect config variables.


Confluent Control Center
---------------

The Confluent Control Center image uses variables prefixed with ``CONTROL_CENTER_`` with an underscore (_) separating each word instead of periods. As an example,

TODO: Sumit add example

Required Settings
"""""""""""""""""

TODO: Sumit add this
