.. _config_reference :

Docker Configuration
====================

You can install the Confluent Platform using Docker images. This section provides an overview of Confluent's Docker images for the Confluent Platform.


.. contents::
    :depth: 2

Confluent Docker Images
-----------------------
The Confluent Platform Docker images support passing configuration variables dynamically using environment variables.  More specifically, we use the Docker ``-e`` or ``--env`` flags for setting various settings in the respective images when starting up the images.

The images are available for Confluent Platform 3.0.1 and greater. Images are available on `DockerHub <https://hub.docker.com/u/confluentinc/>`_ for each component of the Confluent Platform. Alternatively, the source files for the images are `available on Github <https://github.com/confluentinc/cp-docker-images>`_ if you would prefer to extend and/or rebuild the images and upload them to your own DockerHub repository.

The table below lists the available images and the Confluent software packages they contain.  You'll note that some images are identified as ```cp-enterprise-${component_name}```.   These images include proprietary components that must be licensed from Confluent when deployed.

+------------------+------------------------------+--------------+-----------------------------------------+
| Component        | Image Name                   | Type         | Packages Included                       |
+==================+==============================+==============+=========================================+
| Base Image       | cp-base                      | Open Source  | - zulu-openjdk-8                        |
+------------------+------------------------------+--------------+-----------------------------------------+
| Kafka            | cp-kafka                     | Open Source  | - confluent-kafka-*                     |
+------------------+------------------------------+--------------+-----------------------------------------+
| Kafka            | cp-enterprise-kafka          | Enterprise   | - confluent-kafka-*                     |
|                  |                              |              | - confluent-rebalancer                  |
|                  |                              |              | - confluent-support-metrics             |
+------------------+------------------------------+--------------+-----------------------------------------+
| Control Center   | cp-enterprise-control-center | Enterprise   | - confluent-control-center              |
+------------------+------------------------------+--------------+-----------------------------------------+
| Replicator       | cp-enterprise-replicator     | Enterprise   | - confluent-kafka-replicator            |
|                  |                              |              | - confluent-schema-registry             |
|                  |                              |              | - confluent-control-center              |
+------------------+------------------------------+--------------+-----------------------------------------+
| Replicator       | cp-enterprise-replicator     | Enterprise   | - confluent-kafka-replicator            |
| Executable       | -executable                  |              | - confluent-schema-registry             |
|                  |                              |              | - confluent-control-center              |
+------------------+------------------------------+--------------+-----------------------------------------+
| Kafka Connect    | cp-kafka-connect             | Enterprise*  | - confluent-kafka-connect-jdbc          |
|                  |                              |              | - confluent-kafka-connect-hdfs          |
|                  |                              |              | - confluent-schema-registry             |
|                  |                              |              | - confluent-control-center              |
|                  |                              |              | - confluent-kafka-connect-elasticsearch |
|                  |                              |              | - confluent-kafka-connect-s3            |
+------------------+------------------------------+--------------+-----------------------------------------+
| Schema Registry  | cp-schema-registry           | Open Source  | - confluent-schema-registry             |
+------------------+------------------------------+--------------+-----------------------------------------+
| REST Proxy       | cp-kafka-rest                | Open Source  | - confluent-kafka-rest                  |
+------------------+------------------------------+--------------+-----------------------------------------+
| KSQL Server      | cp-ksql-server               | Enterprise*  | - ksql-server                           |
|                  |                              |              | - confluent-monitoring-interceptors     |
+------------------+------------------------------+--------------+-----------------------------------------+
| KSQL CLI         | cp-ksql-cli                  | Open Source  | - ksql-cli                              |
+------------------+------------------------------+--------------+-----------------------------------------+

* Note: The Kafka Connect and KSQL Server images are labeled as "Enterprise" simply because they contain Confluent monitoring interceptors.  The monitoring interceptors enable connectors and KSQL queries to collect the metrics which can be visualized in Confluent Control Center.  The Kafka Connect image includes Confluent Control Center in its entirety, while the KSQL Server image just includes the monitoring interceptors. No explicit license is required when using the Kafka Connect or the KSQL Server image on their own. 

Configuration Notes
-------------------

*  Persistent Data (Mounted Volumes)

	When deploying the Kafka and |zk| images, you should always use `mounted volumes <operations/external-volumes.html>`_ for the file systems those images use for their persistent data.  This ensures that the containers will retain their proper state when stopped and restarted.  The other images maintain their state directly in Kafka topics, so mounted volumes are not usually required for those containers.

*  Bridge Networking vs. Host Networking

	Bridge networking is currently only supported on a single host.  For multiple hosts, you will need to use overlay networks which are not currently supported. To expose Kafka to clients outside of the bridge network, you need to find the container IP and put it in ``advertised.listeners``.  This can be difficult to achieve depending on how you're using the images.  Furthermore, it can add a network hop and may not be as performant as the host network, which shares the network stack.  In summary, host networking is the recommended option in the following cases:

		* Multi-host clusters without using Swarm/Kubernetes host network is the best approach
		* If you need clients to be able to access Kafka outside the bridge/overlay network

*  Adding Connectors to the Kafka Connect Image

	There are currently two ways to add new connectors to the Kafka Connect image.

	* Build a new Docker image that has the connector installed. You can follow the examples found in `Extending Images <development.html#extending-the-docker-images>`_. You will need to make sure that the connector jars are on the CLASSPATH for the Connect service (the default location of /usr/share/java/kafka-connect-* is the recommended location).
	* Add the connector jars via volumes.  If you don't want to create a new Docker image, please see our documentation on `Configuring Kafka Connect with External Jars <operations/external-volumes.html>`_ to configure the `cp-kafka-connect` container with external jars.

*  Included Java

    The Confluent Docker images are tested and shipped with `Azul Zulu OpenJDK <https://www.azul.com/products/zulu/>`_.  Other JDK's (including Oracle Java) are supported, but you must extend the images yourself to implement that change.

*  Untested Features

	The following features/environments are not currently tested:

		* The images are not currently tested on Docker Swarm.

Configuration Parameters
------------------------

Some configuration variables are required when starting up the Docker images.  We have outlined those variables below for each component along with an example of how to pass them.  For a full list of all available configuration options for each Confluent Platform component, you should refer to their respective documentation.

.. contents::
    :depth: 1
    :local:

---------
|zk|
---------

The |zk| image uses variables prefixed with ``ZOOKEEPER_`` with the variables expressed exactly as they would appear in the ``zookeeper.properties`` file.  As an example, to set ``clientPort``, ``tickTime``, and ``syncLimit`` run the command below:

	.. sourcecode:: bash

		docker run -d \
		--net=host \
		--name=zookeeper \
		-e ZOOKEEPER_CLIENT_PORT=32181 \
		-e ZOOKEEPER_TICK_TIME=2000 \
		-e ZOOKEEPER_SYNC_LIMIT=2 \
		confluentinc/cp-zookeeper:4.0.0

Required Settings
"""""""""""""""""

``ZOOKEEPER_CLIENT_PORT``

  This field is always required.  Tells |zk| where to listen for connections by clients such as Kafka.

``ZOOKEEPER_SERVER_ID``

  Only required when running in clustered mode.  Sets the server ID in the ``myid`` file, which consists of a single line containing only the text of that machine's id. So ``myid`` of server 1 would contain the text "1" and nothing else. The id must be unique within the ensemble and should have a value between 1 and 255.

--------------------------
Confluent Kafka (cp-kafka)
--------------------------

The Kafka image uses variables prefixed with ``KAFKA_`` with an underscore (``_``) separating each word instead of periods. As an example, to set ``broker.id``, ``advertised.listeners``, ``zookeeper.connect``, and ``offsets.topic.replication.factor``, you'd run the following command:

  .. sourcecode:: bash

      docker run -d \
          --net=host \
          --name=kafka \
          -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
          -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
          -e KAFKA_BROKER_ID=2 \
          -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
          confluentinc/cp-kafka:4.0.0

  .. note::

    You'll notice that we set the ``KAFKA_ADVERTISED_LISTENERS`` variable to ``localhost:29092``.  This is an important setting, as it will make Kafka accessible from outside the container by advertising its location on the Docker host.

    Also notice that we set ``KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`` to 1.  This is needed when you are running with a single-node cluster.  If you have three or more nodes, you do not need to change this from the default.

Required Settings
"""""""""""""""""

``KAFKA_ZOOKEEPER_CONNECT``

  Tells Kafka how to get in touch with |zk|.

``KAFKA_ADVERTISED_LISTENERS``

  Advertised listeners is required for starting up the Docker image because it is important to think through how other clients are going to connect to kafka.  In a Docker environment, you will need to make sure that your clients can connect to Kafka and other services.  Advertised listeners is how it gives out a host name that can be reached by the client.

------------------------------------------------
Confluent Enterprise Kafka (cp-enterprise-kafka)
------------------------------------------------

The Enterprise Kafka image includes the packages for Confluent Auto Data Balancing and Proactive support in addition to Kafka. The Enterprise Kafka image uses variables prefixed with ``KAFKA_`` for Apache Kafka and with ``CONFLUENT_`` for Confluent components. These variables have an underscore (``_``) separating each word instead of periods. As an example, to set ``broker.id``, ``advertised.listeners``, ``zookeeper.connect``, ``offsets.topic.replication.factor``, and ``confluent.support.customer.id`` you'd run the following command:

  .. sourcecode:: bash

      docker run -d \
          --net=host \
          --name=kafka \
          -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
          -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
          -e KAFKA_BROKER_ID=2 \
          -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
          -e CONFLUENT_SUPPORT_CUSTOMER_ID=c0 \
          confluentinc/cp-enterprise-kafka:4.0.0

  .. note::

    You'll notice that we set the ``KAFKA_ADVERTISED_LISTENERS`` variable to ``localhost:29092``.  This is an important setting, as it will make Kafka accessible from outside the container by advertising its location on the Docker host.

    If you want to enable Proactive support or use Confluent Auto Data Balancing features, please follow the Proactive support and ADB documentation at `Confluent documentation <http://docs.confluent.io/current/>`_.

    Also notice that we set ``KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`` to 1.  This is needed when you are running with a single-node cluster.  If you have three or more nodes, you do not need to change this from the default.


Required Settings
"""""""""""""""""

``KAFKA_ZOOKEEPER_CONNECT``

  Tells Kafka how to get in touch with |zk|.

``KAFKA_ADVERTISED_LISTENERS``

  Advertised listeners is required for starting up the Docker image because it is important to think through how other clients are going to connect to kafka.  In a Docker environment, you will need to make sure that your clients can connect to Kafka and other services.  Advertised listeners is how it gives out a host name that can be reached by the client.


---------------
Schema Registry
---------------

For the Schema Registry image, use variables prefixed with ``SCHEMA_REGISTRY_`` with an underscore (``_``) separating each word instead of periods. As an example, to set ``kafkastore.connection.url``, ``host.name``, ``listeners`` and ``debug`` you'd run the following:

  .. sourcecode:: bash

    docker run -d \
      --net=host \
      --name=schema-registry \
      -e SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL=localhost:32181 \
      -e SCHEMA_REGISTRY_HOST_NAME=localhost \
      -e SCHEMA_REGISTRY_LISTENERS=http://localhost:8081 \
      -e SCHEMA_REGISTRY_DEBUG=true \
      confluentinc/cp-schema-registry:4.0.0

Required Settings
"""""""""""""""""

``SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL``

  |zk| URL for the Kafka cluster.

``SCHEMA_REGISTRY_HOST_NAME``

  The host name advertised in |zk|. Make sure to set this if running Schema Registry with multiple nodes.  Hostname is required because it defaults to the Java canonical host name for the container, which may not always be resolvable in a Docker environment.  Hostname must be resolveable because slave nodes serve registration requests indirectly by simply forwarding them to the current master, and returning the response supplied by the master.  For more information, please refer to the Schema Registry documentation on :ref:`Single Master Architecture <schemaregistry_single_master>`.



----------------
Kafka REST Proxy
----------------

For the Kafka REST Proxy image use variables prefixed with ``KAFKA_REST_`` with an underscore (``_``) separating each word instead of periods. As an example, to set the ``listeners``, ``schema.registry.url`` and ``zookeeper.connect`` you'd run the following command:

  .. sourcecode:: bash

    docker run -d \
      --net=host \
      --name=kafka-rest \
      -e KAFKA_REST_ZOOKEEPER_CONNECT=localhost:32181 \
      -e KAFKA_REST_LISTENERS=http://localhost:8082 \
      -e KAFKA_REST_SCHEMA_REGISTRY_URL=http://localhost:8081 \
      confluentinc/cp-kafka-rest:4.0.0

Required Settings
"""""""""""""""""
The following settings must be passed to run the REST Proxy Docker image.

``KAFKA_REST_HOST_NAME``

  The host name used to generate absolute URLs in responses.  Hostname is required because it defaults to the Java canonical host name for the container, which may not always be resolvable in a Docker environment.  For more details, please refer to the Confluent Platform documentation on :ref:`REST proxy deployment <kafka-rest-deployment>`.

``KAFKA_REST_ZOOKEEPER_CONNECT``

  Specifies the |zk| connection string in the form hostname:port where host and port are the host and port of a |zk| server. To allow connecting through other |zk| nodes when that |zk| machine is down you can also specify multiple hosts in the form hostname1:port1,hostname2:port2,hostname3:port3.

  The server may also have a |zk| ``chroot`` path as part of its |zk| connection string which puts its data under some path in the global |zk| namespace. If so the consumer should use the same chroot path in its connection string. For example to give a chroot path of /chroot/path you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

-------------
Kafka Connect
-------------

The Kafka Connect image uses variables prefixed with ``CONNECT_`` with an underscore (``_``) separating each word instead of periods. As an example, to set the required properties like ``bootstrap.servers``, the topic names for ``config``, ``offsets`` and ``status`` as well the ``key`` or ``value`` converter, run the following command:

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
      -e CONNECT_PLUGIN_PATH=/usr/share/java \
      confluentinc/cp-kafka-connect:4.0.0


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

``CONNECT_PLUGIN_PATH``
  The plugin.path value indicating the location from which to load Connect plugins in classloading isolation.

Optional Settings
"""""""""""""""""
All other settings for Connect like security, monitoring interceptors, producer and consumer overrides can be passed to the Docker images as environment variables. The names of these environment variables are derived by replacing ``.`` with ``_``, converting the resulting string to uppercase and prefixing it with ``CONNECT_``. For example, if you need to set ``ssl.key.password``, the environment variable name would be ``CONNECT_SSL_KEY_PASSWORD``.

The image will then convert these environment variables to corresponding Connect config variables.


------------------------
Confluent Control Center
------------------------

The Confluent Control Center image uses variables prefixed with ``CONTROL_CENTER_`` with an underscore (``_``) separating each word instead of periods. As an example, the following command runs Control Center, passing in its |zk|, Kafka, and Connect configuration parameters.

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
    confluentinc/cp-enterprise-control-center:4.0.0

Docker Options
""""""""""""""

* File descriptor limit:  Control Center may require many open files so we recommend setting the file descriptor limit to at least 16384

* Data persistence: the Control Center image stores its data in the /var/lib/confluent-control-center directory. We recommend that you bind this to a volume on the host machine so that data is persisted across runs.

Required Settings
"""""""""""""""""
The following settings must be passed to run the Confluent Control Center image.

``CONTROL_CENTER_ZOOKEEPER_CONNECT``

  Specifies the |zk| connection string in the form hostname:port where host and port are the host and port of a |zk| server. To allow connecting through other |zk| nodes when that |zk| machine is down you can also specify multiple hosts in the form ``hostname1:port1,hostname2:port2,hostname3:port3``.

  The server may also have a |zk| ``chroot`` path as part of its |zk| connection string which puts its data under some path in the global |zk| namespace. If so the consumer should use the same chroot path in its connection string. For example to give a chroot path of /chroot/path you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

``CONTROL_CENTER_BOOTSTRAP_SERVERS``

  A list of host/port pairs to use for establishing the initial connection to the Kafka cluster. The client will make use of all servers irrespective of which servers are specified here for bootstrapping; this list only impacts the initial hosts used to discover the full set of servers. This list should be in the form host1:port1,host2:port2,.... Since these servers are just used for the initial connection to discover the full cluster membership (which may change dynamically), this list need not contain the full set of servers (you may want more than one, though, in case a server is down).

``CONTROL_CENTER_REPLICATION_FACTOR``

  Replication factor for Control Center topics.  We recommend setting this to 3 in a production environment.

Optional Settings
"""""""""""""""""

``CONTROL_CENTER_CONNECT_CLUSTER``

  To enable Control Center to interact with a Kafka Connect cluster, set this parameter to the REST endpoint URL for the Kafka Connect cluster.

-------------------------------
Confluent Enterprise Replicator
-------------------------------

Confluent Kafka Replicator is a Kafka connector and runs on a Kafka Connect cluster. The image uses variables prefixed with ``CONNECT_`` with an underscore (``_``) separating each word instead of periods. As an example, to set the required properties like ``bootstrap.servers``, the topic names for ``config``, ``offsets`` and ``status`` as well the ``key`` or ``value`` converter, run the following command:

  .. sourcecode:: bash

    docker run -d \
      --name=cp-enterprise-replicator \
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
      confluentinc/cp-enterprise-replicator:4.0.0

The following example shows how to create a Confluent Kafka Replicator connector which replicates topic "confluent" from source Kafka cluster (src) to a destination Kafka cluster (dest).

  .. sourcecode:: bash

    curl -X POST \
         -H "Content-Type: application/json" \
         --data '{
            "name": "confluent-src-to-dest",
            "config": {
              "connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector",
              "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
              "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
              "src.zookeeper.connect": "zookeeper-src:2181",
              "src.kafka.bootstrap.servers": "kafka-src:9082",
              "dest.zookeeper.connect": "zookeeper-dest:2181",
              "topic.whitelist": "confluent",
              "topic.rename.format": "${topic}.replica"}}'  \
                http://localhost:28082/connectors

Required Settings
"""""""""""""""""
The following settings must be passed to run the Kafka Connect Docker image:

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

------------------------------------------
Confluent Enterprise Replicator Executable
------------------------------------------

Confluent Kafka Replicator Executable provides another way to run Replicator by consolidating configuration properties and abstracting Kafka Connect details. The image depends on input files that can be passed by mounting a directory with the expected input files or by mounting each file individually. Additionally, the image supports passing command line parameters to the Replicator executable via environment variables as well. For example:

  .. sourcecode:: bash

    docker run -d \
      --name=ReplicatorX \
      --net=host \
      -e REPLICATOR_LOG4J_ROOT_LOGLEVEL=DEBUG \
      -v /mnt/replicator/config:/etc/replicator \
      confluentinc/cp-enterprise-replicator-executable:4.1.0

will start Replicator given that the local directory ``/mnt/replicator/config``, that will be mounted under ``/etc/replicator`` on the Docker image, contains the required files ``consumer.properties``, ``producer.properties`` and the optional but often necessary file ``replication.properties``.

In a similar example, we start Replicator by omitting to add a ``replication.properties`` and by specifying the replication properties by using environment variables. For a complete list of the expected environment variables see the list of settings in the next sections.

  .. sourcecode:: bash

    docker run -d \
      --name=ReplicatorX \
      --net=host \
      -e CLUSTER_ID=replicator-east-to-west \
      -e WHITELIST=confluent \
      -e TOPIC_RENAME_FORMAT='${topic}.replica' \
      -e REPLICATOR_LOG4J_ROOT_LOGLEVEL=DEBUG \
      -v /mnt/replicator/config:/etc/replicator \
      confluentinc/cp-enterprise-replicator-executable:4.1.0

Required Settings with Defaults
"""""""""""""""""""""""""""""""
The following files must be passed to run the Replicator Executable Docker image:

``CONSUMER_CONFIG``

  A file that contains the configuration settings for the consumer reading from the origin cluster. Default location is ``/etc/replicator/consumer.properties`` in the Docker image.

``PRODUCER_CONFIG``

  A file that contains the configuration settings for the producer writing to the destination cluster. Default location is ``/etc/replicator/producer.properties`` in the Docker image.

``CLUSTER_ID``

  A string that specifies the unique identifier for the Replicator cluster. Default value is ``replicator``.

Optional Settings
"""""""""""""""""

Additional settings that are optional and maybe passed to Replicator Executable via environment variable instead of files are:

``REPLICATION_CONFIG``

  A file that contains the configuration settings for the replication from the origin cluster. Default location is ``/etc/replicator/replication.properties`` in the Docker image.

``CONSUMER_MONITORING_CONFIG``

  A file that contains the configuration settings of the producer writing monitoring information related to Replicator's consumer. Default location is ``/etc/replicator/consumer-monitoring.properties`` in the Docker image.

``PRODUCER_MONITORING_CONFIG``

  A file that contains the configuration settings of the producer writing monitoring information related to Replicator's producer. Default location is ``/etc/replicator/producer-monitoring.properties`` in the Docker image.

``BLACKLIST``

  A comma-separated list of topics that should not be replicated, even if they are included in the whitelist or matched by the regular expression.

``WHITELIST``

  A comma-separated list of the names of topics that should be replicated. Any topic that is in this list and not in the blacklist will be replicated.

``CLUSTER_THREADS``

  The total number of threads across all workers in the Replicator cluster.

``CONFLUENT_LICENSE``

  The Confluent license key. Without the license key, Replicator can be used for a 30-day trial period.

``TOPIC_AUTO_CREATE``

  Whether to automatically create topics in the destination cluster if required.

``TOPIC_CONFIG_SYNC``

  Whether to periodically sync topic configuration to the destination cluster.

``TOPIC_CONFIG_SYNC_INTERVAL_MS``

  How often to check for configuration changes when ``topic.config.sync`` is enabled.

``TOPIC_CREATE_BACKOFF_MS``

  Time to wait before retrying auto topic creation or expansion.

``TOPIC_POLL_INTERVAL_MS``

  Specifies how frequently to poll the source cluster for new topics matching the whitelist or regular expression.

``TOPIC_PRESERVE_PARTITIONS``

  Whether to automatically increase the number of partitions in the destination cluster to match the source cluster and ensure that messages replicated from the source cluster use the same partition in the destination cluster.

``TOPIC_REGEX``

  A regular expression that matches the names of the topics to be replicated. Any topic that matches this expression (or is listed in the whitelist) and not in the blacklist will be replicated.

``TOPIC_RENAME_FORMAT``

  A format string for the topic name in the destination cluster, which may contain ${topic} as a placeholder for the originating topic name.

``TOPIC_TIMESTAMP_TYPE``

  The timestamp type for the topics in the destination cluster.

The above optional, non-file, command line settings as well as any other settings for Replicator can be passed to Replicator Executable through the required or optional files listed above as well.

-----------
KSQL Server
-----------

The KSQL Server image can be configured through environment variables prefixed with ``KSQL_``, uppercasing each word in the parameter name, and separating each word with an underscore (_) instead of periods (.). For example, ``bootstrap.servers`` becomes ``KSQL_BOOTSTRAP_SERVERS``, and ``ksql.service.id``  becomes ``KSQL_KSQL_SERVICE_ID``.

.. sourcecode:: bash

  docker run -d \
    -p 127.0.0.1:8088:8088
    -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
    -e KSQL_LISTENERS=http://0.0.0.0:8088 \
    -e KSQL_KSQL_SERVICE_ID=ksql_test_service_id_ \
    -e KSQL_KSQL_STREAMS_REPLICATION_FACTOR=3 \
    -e KSQL_KSQL_SINK_REPLICAS=3 \
    -e KSQL_KSQL_STREAMS_STATE_DIR=/docker/container/path \
    -v /docker/host/path:/docker/container/path \
    confluentinc/cp-ksql-server:4.1.2

Docker Options
""""""""""""""

* Data persistence: KSQL Server runs Kafka Streams applications which may need to store persistent state locally. The command above maps the state store directory inside the container (cf. ``KSQL_KSQL_STREAMS_STATE_DIR``) to a directory on the Docker host.
* Port mapping: The above command maps the listener port to 8088 on the Docker host, hence ensuring that other containers (like for the KSQL CLI) running on the same host can connect to the KSQL Server container.

Required Settings
"""""""""""""""""
The following settings must be passed to run the KSQL Server image.

``KSQL_BOOTSTRAP_SERVERS``

To configure the Kafka cluster that KSQL should read from/write to, you must specify one or more "bootstrap" brokers from that Kafka cluster. This parameter is formatted as a comma-separated list of hostname:port pairs; for example, ``broker-hostname1:9092,broker-hostname2:9092``. These brokers are used by KSQL to establish the initial connection to the Kafka cluster and to discover the set of all available brokers in the Kafka cluster, the set of which may change dynamically at runtime (e.g. brokers may be taken down for maintenance). You can but don't need to specify all brokers in the Kafka cluster, though it is recommended to specify at least two brokers to make bootstrapping more resilient against individual broker outages.

Optional Settings
"""""""""""""""""
All other settings for KSQL like :ref:`security <ksql-security>`, monitoring interceptors, overrides for Kakfa Streams, Kafka Producer, or Kakfa Consumer settings can be passed to the Docker images as environment variables. The names of these environment variables are derived by prefixing with KSQL_, uppercasing each word in the parameter name, and separating each word with an underscore (_) instead of periods (.). For example, if you need to set ``ksql.streams.state.dir``, the environment variable name would be ``KSQL_KSQL_STREAMS_STATE_DIR``.

The image will then convert these environment variables to corresponding KSQL Server config variables.

--------
KSQL CLI
--------
The KSQL CLI image will execute the ``ksql`` command and try to connect to the server at ``http://localhost:8088`` by default, as shown below. 

.. sourcecode:: bash

  docker run -it -rm confluentinc/cp-ksql-cli:4.1.2

Note: Because the CLI is interactive, the container cannot log to STDOUT as is customary for Docker containers. The KSQL CLI logs can instead be found at /var/logs/ksql-cli/ inside the container.

Configuring the KSQL CLI
""""""""""""""""""""""""
* Config files: Assuming that the CLI's configuration file is available on the Docker host at ``/docker/container/path/ksql-cli.properties``, then the following command will make the configuration file available to the CLI container at ``/docker/container/path/ksql-cli.properties``.

.. sourcecode:: bash
  docker run -it -rm \
    -v /docker/host/path/:/docker/container/path
    confluentinc/cp-ksql-cli:4.1.2 \
      http://ksql-server.host:8088 \
      --config-file /docker/container/path/ksql-cli.properties


* Additional CLI options can be appended to the command as necessary. See :ref:`the KSQL CLI documentation <install_ksql-cli>` for the KSQL CLI options you can use.
* The KSQL CLI cannot be configured via environment variables, unlike the KSQL Server image.

