.. _config_reference :

Configuration
=============

The Confluent Platform Docker images support passing configuration variables dynamically using environment variables.  More specifically, we use the Docker ``-e`` or ``--env`` flags for setting various settings in the respective images when starting up the images.

Some configuration variables are required when starting up the Docker images.  We have outlined those variables below for each component along with an example of how to pass them.  For a full list of all available configuration options for each Confluent Platform component, you should refer to their respective documentation.

	.. note::

		The configuration variable names are prefixed with the name of the component.  For example, the Kafka image will take variables prefixed with ``KAFKA_``.


ZooKeeper
---------

The ZooKeeper image uses variables prefixed with ``ZOOKEEPER_`` with the variables expressed exactly as they would appear in the ``zookeeper.properties`` file.  As an example, to set ``clientPort``, ``tickTime``, and ``syncLimit`` run the command below:

	.. sourcecode:: bash

		docker run -d \
		--net=host \
		--name=zookeeper \
		-e ZOOKEEPER_CLIENT_PORT=32181 \
		-e ZOOKEEPER_TICK_TIME=2000 \
		-e ZOOKEEPER_SYNC_LIMIT=2
		confluentinc/cp-zookeeper:3.1.0

Required Settings
"""""""""""""""""

``ZOOKEEPER_CLIENT_PORT``

  This field is always required.  Tells ZooKeeper where to listen for connections by clients such as Kafka.

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
          confluentinc/cp-kafka:3.1.0

  .. note::

    You'll notice that we set the ``KAFKA_ADVERTISED_LISTENERS`` variable to ``localhost:29092``.  This is an important setting, as it will make Kafka accessible from outside the container by advertising it's location on the Docker host.

Required Settings
"""""""""""""""""

``KAFKA_ZOOKEEPER_CONNECT``

  Tells Kafka how to get in touch with ZooKeeper.

``KAFKA_ADVERTISED_LISTENERS``

  Advertised listeners is required for starting up the Docker image because it is important to think through how other clients are going to connect to kafka.  In a Docker environment, you will need to make sure that your clients can connect to Kafka and other services.  Advertised listeners is how it gives out a host name that can be reached by the client.

Enterprise Kafka
------------------

The Enterprise Kafka image includes the packages for Confluent Auto Data Balancing and Proactive support in addition to Kafka. The Enterprise Kafka image uses variables prefixed with ``KAFKA_`` for Apache Kafka and with ``CONFLUENT_`` for Confluent components. These variables have an underscore (_) separating each word instead of periods. As an example, to set ``broker.id``, ``advertised.listeners``, ``zookeeper.connect``, ``confluent.support.customer.id`` you'd run the following command:

  .. sourcecode:: bash

      docker run -d \
          --net=host \
          --name=kafka \
          -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
          -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
          -e KAFKA_BROKER_ID=2 \
          -e CONFLUENT_SUPPORT_CUSTOMER_ID=c0 \
          confluentinc/cp-enterprise-kafka:3.1.0

  .. note::

    You'll notice that we set the ``KAFKA_ADVERTISED_LISTENERS`` variable to ``localhost:29092``.  This is an important setting, as it will make Kafka accessible from outside the container by advertising it's location on the Docker host.

    If you want to enable Proactive support or use Confluent Auto Data Balancing features, please follow the Proactive support and ADB documentation at `Confluent documentation <http://docs.confluent.io/current/>`_.

Required Settings
"""""""""""""""""

``KAFKA_ZOOKEEPER_CONNECT``

  Tells Kafka how to get in touch with ZooKeeper.

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
      confluentinc/cp-schema-registry:3.1.0

Required Settings
"""""""""""""""""

``SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL``

  ZooKeeper URL for the Kafka cluster.

``SCHEMA_REGISTRY_HOST_NAME``

  The host name advertised in Zookeeper. Make sure to set this if running Schema Registry with multiple nodes.  Hostname is required because it defaults to the Java canonical host name for the container, which may not always be resolvable in a Docker environment.  Hostname must be resolveable because slave nodes serve registration requests indirectly by simply forwarding them to the current master, and returning the response supplied by the master.  For more information, please refer to the Schema Registry documentation on `Single Master Architecture <http://docs.confluent.io/current/schema-registry/docs/design.html#single-master-architecture>`_.


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
      confluentinc/cp-kafka-rest:3.1.0

Required Settings
"""""""""""""""""
The following settings must be passed to run the REST Proxy Docker image.

``KAFKA_REST_HOST_NAME``

  The host name used to generate absolute URLs in responses.  Hostname is required because it defaults to the Java canonical host name for the container, which may not always be resolvable in a Docker environment.  For more details, please refer to the Confluent Platform documentation on `REST proxy deployment <http://docs.confluent.io/current/kafka-rest/docs/deployment.html#deployment>`_.

``KAFKA_REST_ZOOKEEPER_CONNECT``

  Specifies the ZooKeeper connection string in the form hostname:port where host and port are the host and port of a ZooKeeper server. To allow connecting through other ZooKeeper nodes when that ZooKeeper machine is down you can also specify multiple hosts in the form hostname1:port1,hostname2:port2,hostname3:port3.

  The server may also have a ZooKeeper ``chroot`` path as part of it's ZooKeeper connection string which puts its data under some path in the global ZooKeeper namespace. If so the consumer should use the same chroot path in its connection string. For example to give a chroot path of /chroot/path you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

Kafka Connect
---------------

The Kafka Connect image uses variables prefixed with ``CONNECT_`` with an underscore (_) separating each word instead of periods. As an example, to set the required properties like ``bootstrap.servers``, the topic names for ``config``, ``offsets`` and ``status`` as well the ``key`` or ``value`` converter, run the following command:

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
      confluentinc/cp-kafka-connect:3.1.0

Required Settings
"""""""""""""""""
The following settings must be passed to run the Kafka Connect Docker image.

``CONNECT_BOOTSTRAP_SERVERS``

  A unique string that identifies the Connect cluster group this worker belongs to.

``CONNECT_GROUP_ID``

  A unique string that identifies the Connect cluster group this worker belongs to.

``CONNECT_CONFIG_STORAGE_TOPIC``

  The name of the topic in which to store connector and task configuration data. This must be the same for all workers with the same ``group.id``

``CONNECT_OFFSET_STORAGE_TOPIC``

  The name of the topic in which to store offset data for connectors. This must be the same for all workers with the same ``group.id``

``CONNECT_STATUS_STORAGE_TOPIC``

  The name of the topic in which to store state for connectors. This must be the same for all workers with the same ``group.id``

``CONNECT_KEY_CONVERTER``

  Converter class for keys. This controls the format of the data that will be written to Kafka for source connectors or read from Kafka for sink connectors.

``CONNECT_VALUE_CONVERTER``

  Converter class for values. This controls the format of the data that will be written to Kafka for source connectors or read from Kafka for sink connectors.

``CONNECT_INTERNAL_KEY_CONVERTER``

  Converter class for internal keys that implements the ``Converter`` interface.

``CONNECT_INTERNAL_VALUE_CONVERTER``

  Converter class for internal values that implements the ``Converter`` interface.

``CONNECT_REST_ADVERTISED_HOST_NAME``

  Advertised host name is required for starting up the Docker image because it is important to think through how other clients are going to connect to Connect REST API.  In a Docker environment, you will need to make sure that your clients can connect to Connect and other services.  Advertised host name is how Connect gives out a host name that can be reached by the client.

Optional Settings
"""""""""""""""""
All other settings for Connect like security, monitoring interceptors, producer and consumer overrides can be passed to the Docker images as environment variables. The names of these environment variables are derived by replacing ``.`` with ``_``, converting the resulting string to uppercase and prefixing it with ``CONNECT_``. For example, if you need to set ``ssl.key.password``, the environment variable name would be ``CONNECT_SSL_KEY_PASSWORD``.

The image will then convert these environment variables to corresponding Connect config variables.


Confluent Control Center
---------------

The Confluent Control Center image uses variables prefixed with ``CONTROL_CENTER_`` with an underscore (_) separating each word instead of periods. As an example, the following command runs Control Center, passing in its ZooKeeper, Kafka, and Connect configuration parameters.

.. sourcecode:: bash

  docker run -d \
    --net=host \
    --name=control-center \
    --ulimit nofile=16384:16384 \
    -e CONTROL_CENTER_ZOOKEEPER_CONNECT=localhost:32181 \
    -e CONTROL_CENTER_BOOTSTRAP_SERVERS=localhost:29092 \
    -e CONTROL_CENTER_REPLICATION_FACTOR=1 \
    -e CONTROL_CENTER_CONNECT_CLUSTER=http://localhost:28082 \
    -v /mnt/control-center/data:/var/lib/confluent-control-center \
    confluentinc/cp-control-center:3.1.0

Docker Options
""""""""""""""

* File descriptor limit:  Control Center may require many open files so we recommend setting the file descriptor limit to at least 16384

* Data persistence: the Control Center image stores its data in the /var/lib/confluent-control-center directory. We recommend that you bind this to a volume on the host machine so that data is persisted across runs.

Required Settings
"""""""""""""""""
The following settings must be passed to run the Confluent Control Center image.

``CONTROL_CENTER_ZOOKEEPER_CONNECT``

  Specifies the ZooKeeper connection string in the form hostname:port where host and port are the host and port of a ZooKeeper server. To allow connecting through other ZooKeeper nodes when that ZooKeeper machine is down you can also specify multiple hosts in the form ``hostname1:port1,hostname2:port2,hostname3:port3``.

  The server may also have a ZooKeeper ``chroot`` path as part of it's ZooKeeper connection string which puts its data under some path in the global ZooKeeper namespace. If so the consumer should use the same chroot path in its connection string. For example to give a chroot path of /chroot/path you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

``CONTROL_CENTER_BOOTSTRAP_SERVERS``

  A list of host/port pairs to use for establishing the initial connection to the Kafka cluster. The client will make use of all servers irrespective of which servers are specified here for bootstrapping; this list only impacts the initial hosts used to discover the full set of servers. This list should be in the form host1:port1,host2:port2,.... Since these servers are just used for the initial connection to discover the full cluster membership (which may change dynamically), this list need not contain the full set of servers (you may want more than one, though, in case a server is down).

``CONTROL_CENTER_REPLICATION_FACTOR``

  Replication factor for Control Center topics.  We recommend setting this to 3 in a production environment.

Optional Settings
"""""""""""""""""

``CONTROL_CENTER_CONNECT_CLUSTER``

  To enable Control Center to interact with a Kafka Connect cluster, set this parameter to the REST endpoint URL for the Kafka Connect cluster.
