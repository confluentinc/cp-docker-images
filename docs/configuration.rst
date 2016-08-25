.. _configuration :

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
		
		docker run --name zk -e ZOOKEEPER_syncLimit=2 -e ZOOKEEPER__server.1=localhost:2888:3888 confluent/zookeeper.
		docker run -d \
      --net=host \
      --name=zookeeper \
      -e ZOOKEEPER_CLIENT_PORT=32181 \
      -e ZOOKEEPER_TICK_TIME=2000 \
      -e ZOOKEEPER_SYNC_LIMIT=2
      confluentinc/cp-zookeeper:3.0.0

Required Settings
"""""""""""""""""

``ZOOKEEPER_CLIENT_PORT``




Kafka
-----

The Kafka image uses variables prefixed with ``KAFKA_`` with an underscore (_) separating each word instead of periods. As an example, to set ``broker.id`` and ``offsets.storage`` you'd run docker run --name kafka --link zookeeper:zookeeper -e KAFKA_BROKER_ID=2 -e KAFKA_OFFSETS_STORAGE=kafka confluent/kafka.

Required Settings
"""""""""""""""""


advertised hostnames is required because you need to think through how other clients are going to connect to kafka.  in a docker environment you need to make sure that your clients can connect to Kafka and other services.  Advertised Listeners is how it gives out a host name that can be reached by the client.  


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
      confluentinc/cp-schema-registry:3.0.0 

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
      confluentinc/cp-kafka-rest:3.0.0

Required Settings
"""""""""""""""""
The following settings must be passed to run the REST Proxy Docker image.

``KAFKA_REST_LISTENERS``
  Comma-separated list of listeners that listen for API requests over either HTTP or HTTPS. If a listener uses HTTPS, the appropriate SSL configuration parameters need to be set as well.

  * Type: list
  * Default: "http://0.0.0.0:8082"
  * Importance: high

``KAFKA_REST_SCHEMA_REGISTRY_URL``
  The base URL for the schema registry that should be used by the Avro serializer.

``KAFKA_REST_ZOOKEEPER_CONNECT``
  Specifies the ZooKeeper connection string in the form hostname:port where host and port are the host and port of a ZooKeeper server. To allow connecting through other ZooKeeper nodes when that ZooKeeper machine is down you can also specify multiple hosts in the form hostname1:port1,hostname2:port2,hostname3:port3.

  The server may also have a ZooKeeper ``chroot`` path as part of it's ZooKeeper connection string which puts its data under some path in the global ZooKeeper namespace. If so the consumer should use the same chroot path in its connection string. For example to give a chroot path of /chroot/path you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.






