Configuring logging
-------------

All logs are sent to ``stdout`` by default. You can change this by :ref:`extending the images <extending_images>`.

log4j Log Levels
~~~~~~~~~~~~~~~~

To change the default logging levels or add new logging levels:

1. Change the ``{COMPONENT}_LOG4J_ROOT_LOGLEVEL`` to change ``rootLogger`` loglevel.
2. Add or override default loggers by using ``{COMPONENT}_LOG4J_LOGGERS`` environment variable. This variable accepts the comma seperated values of the logger config. For example, to override the log levels of controller and request loggers , use ``KAFKA_LOG4J_LOGGERS="kafka.controller=WARN,kafka.foo.bar=DEBUG"``
3. To change the logging levels for the tools, use the ``{COMPONENT}_LOG4J_TOOLS_ROOT_LOGLEVEL``.

Note: The ``Component Names`` table lists the ``{COMPONENT}`` names for each component.

A full example for Kafka is shown below:

  .. sourcecode:: bash

    docker run -d \
      --name=kafka-log-example \
      --net=host
      -e KAFKA_BROKER_ID=1 \
      -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181/jmx \
      -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:39092 \
      -e KAFKA_JMX_PORT=39999 \
      -e KAFKA_LOG4J_LOGGERS="kafka.controller=WARN,kafka.foo.bar=DEBUG" \
      -e KAFKA_LOG4J_ROOT_LOGLEVEL=WARN \
      -e KAFKA_TOOLS_LOG4J_LOGLEVEL=ERROR \
      confluentinc/cp-kafka:3.1.0


Component Names
~~~~~~~~~~~~~~~~

.. csv-table::
   :header: "Component", "Name"
   :widths: 20, 20

   "Zookeeper", "KAFKA"
   "Kafka", "KAFKA"
   "Confluent Control Center", "CONTROL_CENTER"
   "Schema Registry", "SCHEMA_REGISTRY"
   "REST Proxy", "KAFKA_REST"
   "Kafka Connect", "CONNECT"
