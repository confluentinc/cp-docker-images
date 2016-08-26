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

The Kafka Connect image uses variables prefixed with ``KAFKA_CONNECT_`` with an underscore (_) separating each word instead of periods. As an example....

TODO: Sumit add example

Required Settings
"""""""""""""""""

TODO: Sumit add this

Confluent Control Center
---------------

The Confluent Control Center image uses variables prefixed with ``CONTROL_CENTER_`` with an underscore (_) separating each word instead of periods. As an example,

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
    confluentinc/cp-control-center:3.0.1

Docker Options
""""""""""""""

* File descriptor limit:  Control Center may require many open files so we recommend setting the file descriptor limit to at least 16384

* Data persistence: the Control Center image stores it's data in the /var/lib/confluent-control-center directory. We recommend that you bind this to a volume on the host machine so that data is persisted across runs.

Required Settings
"""""""""""""""""
The following settings must be passed to run the Confluent Control Center image.

``CONTROL_CENTER_ZOOKEEPER_CONNECT``

  Specifies the ZooKeeper connection string in the form hostname:port where host and port are the host and port of a ZooKeeper server. To allow connecting through other ZooKeeper nodes when that ZooKeeper machine is down you can also specify multiple hosts in the form hostname1:port1,hostname2:port2,hostname3:port3.

  The server may also have a ZooKeeper ``chroot`` path as part of it's ZooKeeper connection string which puts its data under some path in the global ZooKeeper namespace. If so the consumer should use the same chroot path in its connection string. For example to give a chroot path of /chroot/path you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

``CONTROL_CENTER_BOOTSTRAP_SERVERS``

  A list of host/port pairs to use for establishing the initial connection to the Kafka cluster. The client will make use of all servers irrespective of which servers are specified here for bootstrapping; this list only impacts the initial hosts used to discover the full set of servers. This list should be in the form host1:port1,host2:port2,.... Since these servers are just used for the initial connection to discover the full cluster membership (which may change dynamically), this list need not contain the full set of servers (you may want more than one, though, in case a server is down).

``CONTROL_CENTER_REPLICATION_FACTOR``

  Replication factor for Control Center topics.  We recommend setting this to 3 in a production environment.

Optional Settings
"""""""""""""""""

``CONTROL_CENTER_CONNECT_CLUSTER``

  To enable Control Center to interact with a Kafka Connect cluster, set this parameter to the REST endpoint URL for the Kafka Connect cluster.
