.. _config_reference:

Docker Configuration Parameters
===============================

This topic describes how to configure the Docker images when starting |cp|.

You can dynamically specify configuration values in the |cp| Docker images with environment variables. You can use the
Docker ``-e`` or ``--env`` flags for to specify various settings.

------------------
|zk| Configuration
------------------

The |zk| (``cp-zookeeper``) image uses variables prefixed with ``ZOOKEEPER_`` with the variables expressed exactly as they would appear in
the ``zookeeper.properties`` file.  As an example, to set ``clientPort``, ``tickTime``, and ``syncLimit`` run the command below:

.. codewithvars:: bash

    docker run -d \
    --net=host \
    --name=zookeeper \
    -e ZOOKEEPER_CLIENT_PORT=32181 \
    -e ZOOKEEPER_TICK_TIME=2000 \
    -e ZOOKEEPER_SYNC_LIMIT=2 \
    confluentinc/cp-zookeeper:|release|

Required |zk| Settings
""""""""""""""""""""""

These are the required |zk| settings. Some are only required, dependent on your configuration.

``ZOOKEEPER_CLIENT_PORT``
    Instructs |zk| where to listen for connections by clients such as Kafka.

``ZOOKEEPER_SERVER_ID``
    This is only required when running in clustered mode.  Sets the server ID in the ``myid`` file, which consists of a single
    line that contains only the text of that machine's ID. For example, the ``myid`` of server 1 would only contain the text ``"1"``.
    The ID must be unique within the ensemble and should have a value between 1 and 255.

-----------------------------
Confluent Kafka Configuration
-----------------------------

The Kafka (``cp-kafka``) image uses variables prefixed with ``KAFKA_`` with an underscore (``_``) separating each word. For example,
run the following commands to set ``broker.id``, ``advertised.listeners``, ``zookeeper.connect``, and
``offsets.topic.replication.factor``:

.. codewithvars:: bash

  docker run -d \
      --net=host \
      --name=kafka \
      -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
      -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
      -e KAFKA_BROKER_ID=2 \
      -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
      confluentinc/cp-kafka:|release|

.. note:: The ``KAFKA_ADVERTISED_LISTENERS`` variable is set to ``localhost:29092``.  This makes Kafka accessible from
          outside the container by advertising its location on the Docker host.

.. include:: includes/config-shared.rst
    :start-line: 2
    :end-line: 4

Required Confluent Kafka Settings
"""""""""""""""""""""""""""""""""

``KAFKA_ZOOKEEPER_CONNECT``
    Instructs Kafka how to get in touch with |zk|.

.. include:: includes/config-shared.rst
    :start-line: 7
    :end-line: 13

----------------------------------------
Confluent Enterprise Kafka Configuration
----------------------------------------

The Enterprise Kafka (``cp-enterprise-kafka``) image includes the packages for Confluent Auto Data Balancing and Proactive support in addition to
Kafka. The Enterprise Kafka image uses variables prefixed with ``KAFKA_`` for Apache Kafka and with ``CONFLUENT_`` for
Confluent components. These variables have an underscore (``_``) that seperates each word. For example,
run this command to set ``broker.id``, ``advertised.listeners``, ``zookeeper.connect``, ``offsets.topic.replication.factor``,
and ``confluent.support.customer.id``:

.. codewithvars:: bash

  docker run -d \
      --net=host \
      --name=kafka \
      -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181 \
      -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
      -e KAFKA_BROKER_ID=2 \
      -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
      -e CONFLUENT_SUPPORT_CUSTOMER_ID=c0 \
      confluentinc/cp-enterprise-kafka:|release|

.. note:: The ``KAFKA_ADVERTISED_LISTENERS`` variable is set to ``localhost:29092``.  It makes Kafka accessible from outside
          of the container by advertising its location on the Docker host.

If you want to enable Proactive support or use Confluent Auto Data Balancing features, see :ref:`cp-proactive-support` and
:ref:`rebalancer`.

.. include:: includes/config-shared.rst
    :start-line: 2
    :end-line: 4


Required Confluent Enterprise Kafka Settings
""""""""""""""""""""""""""""""""""""""""""""

``KAFKA_ZOOKEEPER_CONNECT``
    Tells Kafka how to get in touch with |zk|.

.. include:: includes/config-shared.rst
    :start-line: 7
    :end-line: 13


-----------------------------
Schema Registry Configuration
-----------------------------

For the |sr| (``cp-schema-registry``) image, use variables prefixed with ``SCHEMA_REGISTRY_`` with an
underscore (``_``) to separate each word. For example, run the following to set ``kafkastore.connection.url``, ``host.name``,
``listeners`` and ``debug``:

.. codewithvars:: bash

    docker run -d \
      --net=host \
      --name=schema-registry \
      -e SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL=localhost:32181 \
      -e SCHEMA_REGISTRY_HOST_NAME=localhost \
      -e SCHEMA_REGISTRY_LISTENERS=http://localhost:8081 \
      -e SCHEMA_REGISTRY_DEBUG=true \
      confluentinc/cp-schema-registry:|release|

Required Schema Registry Settings
"""""""""""""""""""""""""""""""""

``SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL``
    |zk| URL for the Kafka cluster.

``SCHEMA_REGISTRY_HOST_NAME``
    The hostname advertised in |zk|. This is required if if you are running Schema Registry with multiple nodes. Hostname is
    required because it defaults to the Java canonical hostname for the container, which may not always be resolvable in a
    Docker environment.  Hostname must be resolveable because slave nodes serve registration requests indirectly by simply
    forwarding them to the current master, and returning the response supplied by the master.  For more information, see the
    Schema Registry documentation on :ref:`Single Master Architecture <schemaregistry_single_master>`.

------------------------------
Kafka REST Proxy Configuration
------------------------------
The variables used in the Kafka REST Proxy (``cp-kafka-rest``) image are prefixed with ``KAFKA_REST_``, with an underscore
(``_``) that separates each word. For example, run this command to set the ``listeners``, ``schema.registry.url`` and
``zookeeper.connect``:

.. codewithvars:: bash

    docker run -d \
      --net=host \
      --name=kafka-rest \
      -e KAFKA_REST_ZOOKEEPER_CONNECT=localhost:32181 \
      -e KAFKA_REST_LISTENERS=http://localhost:8082 \
      -e KAFKA_REST_SCHEMA_REGISTRY_URL=http://localhost:8081 \
      confluentinc/cp-kafka-rest:|release|

Required Kafka REST Proxy Settings
""""""""""""""""""""""""""""""""""

The following settings must be passed to run the REST Proxy Docker image.

``KAFKA_REST_HOST_NAME``
    The hostname used to generate absolute URLs in responses.  Hostname is required because it defaults to the Java canonical
    hostname for the container, which may not always be resolvable in a Docker environment.  For more information, see the |cp|
    documentation on :ref:`REST proxy deployment <kafka-rest-deployment>`.

``KAFKA_REST_ZOOKEEPER_CONNECT``
    The |zk| connection string in the form ``hostname:port`` where host and port are the host and port of a |zk| server. To
    allow connecting through other |zk| nodes when that |zk| machine is down you can also specify multiple hosts in the form
    ``hostname1:port1,hostname2:port2,hostname3:port3``.

    The server may also have a |zk| ``chroot`` path as part of its |zk| connection string which puts its data under some path
    in the global |zk| namespace. If so the consumer should use the same chroot path in its connection string. For example to
    give a chroot path of ``/chroot/path`` you would give the connection string as ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

---------------------------
Kafka Connect Configuration
---------------------------

The variables used in the Kafka Connect (``cp-kafka-connect``) image are prefixed with ``CONNECT_``, with an underscore (``_``) that separates
each word. For example, run this command to set the required properties like ``bootstrap.servers``,
the topic names for ``config``, ``offsets`` and ``status`` as well the ``key`` or ``value`` converter:

.. codewithvars:: bash

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
      confluentinc/cp-kafka-connect:|release|


Required Kafka Connect Settings
"""""""""""""""""""""""""""""""
The following settings must be passed to run the Kafka Connect Docker image.

``CONNECT_BOOTSTRAP_SERVERS``
    A unique string that identifies the Connect cluster group this worker belongs to.

``CONNECT_GROUP_ID``
    A unique string that identifies the Connect cluster group this worker belongs to.

``CONNECT_CONFIG_STORAGE_TOPIC``
    The name of the topic in which to store connector and task configuration data. This must be the same for all workers with
    the same ``group.id``

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
    The hostname that is given out to other workers to connect to. In a Docker environment, your clients must be able to connect
    to the Connect and other services.  Advertised hostname is how Connect gives out a hostname that can be reached by the client.

``CONNECT_PLUGIN_PATH``
    The plugin.path value that indicates the location from which to load Connect plugins in classloading isolation.

Optional Kafka Connect Settings
"""""""""""""""""""""""""""""""
All other settings for Connect like security, monitoring interceptors, producer and consumer overrides can be passed to
the Docker images as environment variables. The names of these environment variables are derived by replacing ``.`` with ``_``,
converting the resulting string to uppercase and prefixing it with ``CONNECT_``. For example, if you need to set
``ssl.key.password``, the environment variable name would be ``CONNECT_SSL_KEY_PASSWORD``.

The image will then convert these environment variables to corresponding Connect config variables.

------------------
|c3| Configuration
------------------

The |c3| (``cp-control-center``) image uses variables prefixed with ``CONTROL_CENTER_`` with an underscore (``_``) that separates each word, instead
of periods. For example, the following command runs |c3-short|, passing in its |zk|, Kafka, and Connect configuration parameters.

.. codewithvars:: bash

  docker run -d \
    --net=host \
    --name=control-center \
    --ulimit nofile=16384:16384 \
    -e CONTROL_CENTER_ZOOKEEPER_CONNECT=localhost:32181 \
    -e CONTROL_CENTER_BOOTSTRAP_SERVERS=localhost:29092 \
    -e CONTROL_CENTER_REPLICATION_FACTOR=1 \
    -e CONTROL_CENTER_CONNECT_CLUSTER=http://localhost:28082 \
    -v /mnt/control-center/data:/var/lib/confluent-control-center \
    confluentinc/cp-enterprise-control-center:|release|

|c3-short| Docker Options
"""""""""""""""""""""""""

* File descriptor limit:  |c3-short| may require many open files so we recommend setting the file descriptor limit to at least 16384

* Data persistence: the |c3-short| image stores its data in the /var/lib/confluent-control-center directory. We recommend that you bind this to a volume on the host machine so that data is persisted across runs.

|c3-short| Required Settings
""""""""""""""""""""""""""""
The following settings must be passed to run the |c3| image.

``CONTROL_CENTER_ZOOKEEPER_CONNECT``
    Specifies the |zk| connection string in the form hostname:port where host and port are the host and port of a |zk| server.
    To allow connecting through other |zk| nodes when that |zk| machine is down you can also specify multiple hosts in the form
    ``hostname1:port1,hostname2:port2,hostname3:port3``.

    The server may also have a |zk| ``chroot`` path as part of its |zk| connection string which puts its data under some path
    in the global |zk| namespace. If so the consumer should use the same chroot path in its connection string. For example to
    give a chroot path of /chroot/path you would give the connection string as
    ``hostname1:port1,hostname2:port2,hostname3:port3/chroot/path``.

``CONTROL_CENTER_BOOTSTRAP_SERVERS``
    A list of host/port pairs to use for establishing the initial connection to the Kafka cluster. The client will use
    all servers irrespective of which servers are specified here for bootstrapping; this list only impacts the initial hosts
    used to discover the full set of servers. This list should be in the form ``host1:port1,host2:port2,....`` Since these servers
    are only used for the initial connection to discover the full cluster membership (which may change dynamically), this list
    does not require the full set of servers. You might want more than one, in case a server is down.

``CONTROL_CENTER_REPLICATION_FACTOR``
    Replication factor for |c3-short| topics.  We recommend setting this to 3 in a production environment.

|c3-short| Optional Settings
""""""""""""""""""""""""""""

``CONTROL_CENTER_CONNECT_CLUSTER``
    To enable |c3-short| to interact with a Kafka Connect cluster, set this parameter to the REST endpoint URL for the Kafka Connect cluster.

---------------------------------------------
Confluent Enterprise Replicator Configuration
---------------------------------------------

Confluent Kafka Replicator is a Kafka connector and runs on a Kafka Connect cluster. The image (``cp-enterprise-replicator``)
uses variables prefixed with ``CONNECT_`` with an underscore (``_``) separating each word. For example, run the following
commands to set the required properties like ``bootstrap.servers``, the topic names for ``config``, ``offsets`` and ``status``
and the ``key`` or ``value`` converter:

.. codewithvars:: bash

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
      confluentinc/cp-enterprise-replicator:|release|

The following example shows how to create a Confluent Kafka Replicator connector which replicates topic "confluent" from
source Kafka cluster (src) to a destination Kafka cluster (dest).

.. codewithvars:: bash

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

Required Confluent Enterprise Replicator Settings
"""""""""""""""""""""""""""""""""""""""""""""""""
The following settings must be passed to run the Kafka Connect Docker image:

``CONNECT_BOOTSTRAP_SERVERS``
    A unique string that identifies the Connect cluster group this worker belongs to.

``CONNECT_GROUP_ID``
    A unique string that identifies the Connect cluster group this worker belongs to.

``CONNECT_CONFIG_STORAGE_TOPIC``
    The name of the topic where connector and task configuration data is stored. This must be the same for all workers with the same ``group.id``

``CONNECT_OFFSET_STORAGE_TOPIC``
    The name of the topic where offset data for connectors is stored. This must be the same for all workers with the same ``group.id``

``CONNECT_STATUS_STORAGE_TOPIC``
    The name of the topic where state for connectors is stored. This must be the same for all workers with the same ``group.id``

``CONNECT_KEY_CONVERTER``
    Converter class for keys. This controls the format of the data that will be written to Kafka for source connectors or read from Kafka for sink connectors.

``CONNECT_VALUE_CONVERTER``
    Converter class for values. This controls the format of the data that will be written to Kafka for source connectors or read from Kafka for sink connectors.

``CONNECT_INTERNAL_KEY_CONVERTER``
    Converter class for internal keys that implements the ``Converter`` interface.

``CONNECT_INTERNAL_VALUE_CONVERTER``
    Converter class for internal values that implements the ``Converter`` interface.

``CONNECT_REST_ADVERTISED_HOST_NAME``
    The hostname that will be given out to other workers to connect to. In a Docker environment, your clients must be able to connect
    to the Connect and other services.  Advertised hostname is how Connect gives out a hostname that can be reached by the client.

Optional Confluent Enterprise Replicator Settings
"""""""""""""""""""""""""""""""""""""""""""""""""
All other settings for Connect like security, monitoring interceptors, producer and consumer overrides can be passed to
the Docker images as environment variables. The names of these environment variables are derived by replacing ``.`` with
``_``, converting the resulting string to uppercase and prefixing it with ``CONNECT_``. For example, if you must set
``ssl.key.password``, the environment variable name would be ``CONNECT_SSL_KEY_PASSWORD``.

The image will then convert these environment variables to corresponding Connect config variables.

--------------------------------------------------------
Confluent Enterprise Replicator Executable Configuration
--------------------------------------------------------

Confluent Kafka Replicator Executable (``cp-enterprise-replicator-executable``) provides another way to run Replicator by consolidating configuration properties and abstracting Kafka Connect details. The image depends on input files that can be passed by mounting a directory with the expected input files or by mounting each file individually. Additionally, the image supports passing command line parameters to the Replicator executable via environment variables as well. For example:

  .. codewithvars:: bash

    docker run -d \
      --name=ReplicatorX \
      --net=host \
      -e REPLICATOR_LOG4J_ROOT_LOGLEVEL=DEBUG \
      -v /mnt/replicator/config:/etc/replicator \
      confluentinc/cp-enterprise-replicator-executable:|release|

will start Replicator given that the local directory ``/mnt/replicator/config``, that will be mounted under ``/etc/replicator`` on the Docker image, contains the required files ``consumer.properties``, ``producer.properties`` and the optional but often necessary file ``replication.properties``.

In a similar example, we start Replicator by omitting to add a ``replication.properties`` and by specifying the replication properties by using environment variables. For a complete list of the expected environment variables see the list of settings in the next sections.

  .. codewithvars:: bash

    docker run -d \
      --name=ReplicatorX \
      --net=host \
      -e CLUSTER_ID=replicator-east-to-west \
      -e WHITELIST=confluent \
      -e TOPIC_RENAME_FORMAT='${topic}.replica' \
      -e REPLICATOR_LOG4J_ROOT_LOGLEVEL=DEBUG \
      -v /mnt/replicator/config:/etc/replicator \
      confluentinc/cp-enterprise-replicator-executable:|release|

Required Confluent Enterprise Replicator Executable Settings
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
The following files must be passed to run the Replicator Executable Docker image:

``CONSUMER_CONFIG``
    A file that contains the configuration settings for the consumer reading from the origin cluster. Default location is ``/etc/replicator/consumer.properties`` in the Docker image.

``PRODUCER_CONFIG``
    A file that contains the configuration settings for the producer writing to the destination cluster. Default location is ``/etc/replicator/producer.properties`` in the Docker image.

``CLUSTER_ID``
    A string that specifies the unique identifier for the Replicator cluster. Default value is ``replicator``.

Optional Confluent Enterprise Replicator Executable Settings
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

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
    If you disable automatic topic creation, Kafka Streams and KSQL applications
    continue to work. Kafka Streams and KSQL applications use the Admin Client,
    so topics are still created.

``TOPIC_CONFIG_SYNC``
    Whether to periodically sync topic configuration to the destination cluster.

``TOPIC_CONFIG_SYNC_INTERVAL_MS``
    Specifies how frequently to check for configuration changes when ``topic.config.sync`` is enabled.

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

For a complete list of KSQL parameters, see :ref:`KSQL Configuration Parameter Reference <ksql-param-reference>`.

KSQL Headless Server Settings
"""""""""""""""""""""""""""""

Run a standalone KSQL Server instance in a container.

``KSQL_BOOTSTRAP_SERVERS``
    A list of hosts for establishing the initial connection to the Kafka
    cluster.  

``KSQL_KSQL_SERVICE_ID``
    The service ID of the KSQL server, which is used as the prefix for the
    internal topics created by KSQL.

``KSQL_KSQL_QUERIES_FILE``
    A file that specifies predefined KSQL queries.

.. codewithvars:: bash

  docker run -d \
    -v /path/on/host:/path/in/container/ \
    -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
    -e KSQL_KSQL_SERVICE_ID=confluent_standalone_2_ \
    -e KSQL_KSQL_QUERIES_FILE=/path/in/container/queries.sql \
    confluentinc/cp-ksql-server:|release|

KSQL Headless Server with Interceptors Settings
"""""""""""""""""""""""""""""""""""""""""""""""

Run a standalone KSQL Server with specified interceptor classes in a container.
For more info on interceptor classes, see :ref:`Confluent Monitoring Interceptors <controlcenter_clients>`.

``KSQL_BOOTSTRAP_SERVERS``
    A list of hosts for establishing the initial connection to the Kafka
    cluster. 

``KSQL_KSQL_SERVICE_ID``
    The service ID of the KSQL server, which is used as the prefix for the
    internal topics created by KSQL.

``KSQL_KSQL_QUERIES_FILE``
    A file that specifies predefined KSQL queries.

``KSQL_PRODUCER_INTERCEPTOR_CLASSES``
    A list of fully qualified class names for producer interceptors.

``KSQL_CONSUMER_INTERCEPTOR_CLASSES``
    A list of fully qualified class names for consumer interceptors.

.. codewithvars:: bash

  docker run -d \
    -v /path/on/host:/path/in/container/ \
    -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
    -e KSQL_KSQL_SERVICE_ID=confluent_standalone_2_ \
    -e KSQL_PRODUCER_INTERCEPTOR_CLASSES=io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor \
    -e KSQL_CONSUMER_INTERCEPTOR_CLASSES=io.confluent.monitoring.clients.interceptor.MonitoringConsumerInterceptor \
    -e KSQL_KSQL_QUERIES_FILE=/path/in/container/queries.sql \
    confluentinc/cp-ksql-server:|release|

Interactive Server Configuration
""""""""""""""""""""""""""""""""

Run a KSQL Server that enables manual interaction by using the KSQL CLI.

``KSQL_BOOTSTRAP_SERVERS``
    A list of hosts for establishing the initial connection to the Kafka
    cluster. 

``KSQL_KSQL_SERVICE_ID``
    The service ID of the KSQL server, which is used as the prefix for the
    internal topics created by KSQL.

``KSQL_LISTENERS``
    A list of URIs, including the protocol, that the broker listens on.

.. codewithvars:: bash

  docker run -d \
    -p 127.0.0.1:8088:8088 \
    -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
    -e KSQL_LISTENERS=http://0.0.0.0:8088/ \
    -e KSQL_KSQL_SERVICE_ID=confluent_test_2 \
    confluentinc/cp-ksql-server:|release|

Interactive Server Configuration with Interceptors
""""""""""""""""""""""""""""""""""""""""""""""""""

Run a KSQL Server with interceptors that enables manual interaction by using
the KSQL CLI. For more info on interceptor classes, see
:ref:`Confluent Monitoring Interceptors <controlcenter_clients>`.

``KSQL_BOOTSTRAP_SERVERS``
    A list of hosts for establishing the initial connection to the Kafka
    cluster.

``KSQL_KSQL_SERVICE_ID``
    The service ID of the KSQL server, which is used as the prefix for the
    internal topics created by KSQL.

``KSQL_LISTENERS``
    A list of URIs, including the protocol, that the broker listens on.    

``KSQL_PRODUCER_INTERCEPTOR_CLASSES``
    A list of fully qualified class names for producer interceptors.

``KSQL_CONSUMER_INTERCEPTOR_CLASSES``
    A list of fully qualified class names for consumer interceptors.

.. codewithvars:: bash

  docker run -d \
    -p 127.0.0.1:8088:8088 \
    -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
    -e KSQL_LISTENERS=http://0.0.0.0:8088/ \
    -e KSQL_KSQL_SERVICE_ID=confluent_test_2_ \
    -e KSQL_PRODUCER_INTERCEPTOR_CLASSES=io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor \
    -e KSQL_CONSUMER_INTERCEPTOR_CLASSES=io.confluent.monitoring.clients.interceptor.MonitoringConsumerInterceptor \
    confluentinc/cp-ksql-server:|release|

In interactive mode, the CLI instance running outside Docker can connect to the
server running in Docker.

.. codewithvars:: bash

  ./bin/ksql

  ... 
  CLI v|release|, Server v|release|-SNAPSHOT located at http://localhost:8088

  Having trouble? Type 'help' (case-insensitive) for a rundown of how things work!

  ksql>

Connect to a Secure Kafka Cluster, Like |ccloud|
""""""""""""""""""""""""""""""""""""""""""""""""

Run a KSQL Server that uses a secure connection to a Kafka cluster. 
Learn about :ref:`KSQL Security <ksql-security>`.

``KSQL_BOOTSTRAP_SERVERS``
    A list of hosts for establishing the initial connection to the Kafka
    cluster. 

``KSQL_KSQL_SERVICE_ID``
    The service ID of the KSQL server, which is used as the prefix for the
    internal topics created by KSQL.

``KSQL_LISTENERS``
    A list of URIs, including the protocol, that the broker listens on.
    
``KSQL_KSQL_SINK_REPLICAS``
    The default number of replicas for the topics created by KSQL.
    The default is one.

``KSQL_KSQL_STREAMS_REPLICATION_FACTOR``
    The replication factor for internal topics, the command topic, and output
    topics. 

``KSQL_SECURITY_PROTOCOL``
    The protocol that your Kafka cluster uses for security.

``KSQL_SASL_MECHANISM``
    The SASL mechanism that your Kafka cluster uses for security.

``KSQL_SASL_JAAS_CONFIG``
    The Java Authentication and Authorization Service (JAAS) configuration.

.. codewithvars:: bash

  docker run -d \
    -p 127.0.0.1:8088:8088 \
    -e KSQL_BOOTSTRAP_SERVERS=REMOVED_SERVER1:9092,REMOVED_SERVER2:9093,REMOVED_SERVER3:9094 \
    -e KSQL_LISTENERS=http://0.0.0.0:8088/ \
    -e KSQL_KSQL_SERVICE_ID=default_ \
    -e KSQL_KSQL_SINK_REPLICAS=3 \
    -e KSQL_KSQL_STREAMS_REPLICATION_FACTOR=3 \
    -e KSQL_SECURITY_PROTOCOL=SASL_SSL \
    -e KSQL_SASL_MECHANISM=PLAIN \
    -e KSQL_SASL_JAAS_CONFIG="org.apache.kafka.common.security.plain.PlainLoginModule required username=\"<username>\" password=\"<strong-password>\";" \
    confluentinc/cp-ksql-server:|release|

Configure a KSQL Server by Using Java System Properties
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

Run a KSQL Server with a configration that's defined by Java properties.  

``KSQL_BOOTSTRAP_SERVERS``
    A list of hosts for establishing the initial connection to the Kafka
    cluster.

``KSQL_OPTS``
    A space-separated list of Java options.

.. codewithvars:: bash

  docker run -d \
    -v /path/on/host:/path/in/container/ \
    -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
    -e KSQL_OPTS="-Dksql.service.id=confluent_test_3_  -Dksql.queries.file=/path/in/container/queries.sql" \
    confluentinc/cp-ksql-server:|release|

View logs
"""""""""

Use the ``docker logs`` command to view KSQL logs that are generated from 
within the container.

.. codewithvars:: bash

  docker logs -f <container-id>
  [2018-05-24 23:43:05,591] INFO stream-thread [_confluent-ksql-default_transient_1507119262168861890_1527205385485-71c8a94c-abe9-45ba-91f5-69a762ec5c1d-StreamThread-17] Starting (org.apache.kafka.streams.processor.internals.StreamThread:713)
  ...

--------
KSQL CLI
--------

Connect to a Dockerized KSQL Server
"""""""""""""""""""""""""""""""""""

Run a KSQL CLI instance in a container and connect to a KSQL Server that's
running in a container.

The Docker network created by KSQL Server enables you to connect to a
dockerized KSQL server.

``KSQL_BOOTSTRAP_SERVERS``
    A list of hosts for establishing the initial connection to the Kafka
    cluster.

``KSQL_OPTS``
    A space-separated list of Java options.

.. codewithvars:: bash

  # Run KSQL Server.
  docker run -d -p 10.0.0.11:8088:8088 \
    -e KSQL_BOOTSTRAP_SERVERS=localhost:9092 \
    -e KSQL_OPTS="-Dksql.service.id=confluent_test_3_  -Dlisteners=http://0.0.0.0:8088/" \  
    confluentinc/cp-ksql-server:|release|

  # Connect the KSQL CLI to the server.
  docker run -it confluentinc/cp-ksql-cli http://10.0.0.11:8088 
  ...
  Copyright 2017 Confluent Inc.

  CLI v|release|-SNAPSHOT, Server v|release|-SNAPSHOT located at http://10.0.0.11:8088

  Having trouble? Type 'help' (case-insensitive) for a rundown of how things work!

  ksql>


Provide a Configuration File
""""""""""""""""""""""""""""

Set up a a KSQL CLI instance by using a configuration file, and run it in a
container. 


.. codewithvars:: bash

  # Assume KSQL Server is running.
  # Ensure that the configuration file exists.
  ls /path/on/host/ksql-cli.properties

  docker run -it \
    -v /path/on/host/:/path/in/container  \
    confluentinc/cp-ksql-cli:|release| http://10.0.0.11:8088 \
    --config-file /path/in/container/ksql-cli.properties

Connect to a KSQL Server Running on Another Host, Like AWS
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Run a KSQL CLI instance in a container and connect to a remote KSQL Server host.

.. codewithvars:: bash

  docker run -it confluentinc/cp-ksql-cli:|release| \
    http://ec2-etc.us-etc.compute.amazonaws.com:8080

  ... 
  Copyright 2017 Confluent Inc.

  CLI v|release|-SNAPSHOT, Server v|release|-SNAPSHOT located at http://ec2-blah.us-blah.compute.amazonaws.com:8080

  Having trouble? Type 'help' (case-insensitive) for a rundown of how things work!

  ksql>

