Monitoring
---------


Using JMX
~~~~~~~~~~~~~

For JMX to work with docker containers, the following properties must be set:

  .. sourcecode:: bash

    java.rmi.server.hostname=<JMX_HOSTNAME>
    com.sun.management.jmxremote.local.only=false
    com.sun.management.jmxremote.rmi.port=<JMX_PORT>
    com.sun.management.jmxremote.port=<JMX_PORT>

Note about ``hostname``:

  The JMX client needs to be able to connect to ``java.rmi.server.hostname``.
  The default for bridged network is the bridged IP so you will only be able to connect from another docker container.
  For host network, this is the IP that the hostname on the host resolves to.

  The hostname is set to ``hostname -i`` in the docker container. If you have more that one network configured for the container, ``hostname -i`` gives you all the IPs, the default is to pick the first IP (or network).

Security
"""""""""

To set security on JMX, you can follow the SSL and authentication sections in this guide: https://docs.oracle.com/javase/8/docs/technotes/guides/management/agent.html

Kafka & Zookeeper
"""""""""""""""""

Properties
``````````

  ``KAFKA_JMX_PORT``
    JMX Port.


  ``KAFKA_JMX_OPTS``
    JMX options.

    The default setting is as follows:

    .. sourcecode:: bash
    
      -Dcom.sun.management.jmxremote=true -Dcom.sun.management.jmxremote.authenticate=false  -Dcom.sun.management.jmxremote.ssl=false

Launching Kafka and Zookeeper with JMX Enabled
``````````````````````````````````````````````

The steps for launching Kafka and Zookeeper with JMX enabled are the same as we saw in the `quickstart guide <quickstart.html>`, with the only difference being that you set the ``KAFKA_JMX_PORT`` for both.  Here are examples of the Docker ``run`` commands for each service:

.. sourcecode:: bash

  docker run -d \
    --name=zk-jmx \
    --net=host \
    -e ZOOKEEPER_TICK_TIME=2000 \
    -e ZOOKEEPER_CLIENT_PORT=52181 \
    -e KAFKA_JMX_PORT=49999 \
    confluentinc/cp-zookeeper:3.0.0


  docker run -d \
    --name=kafka-jmx \
    --net=host \
    -e KAFKA_BROKER_ID=1 \
    -e KAFKA_ZOOKEEPER_CONNECT=localhost:32181/jmx \
    -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:39092 \
    -e KAFKA_JMX_PORT=39999 \
    confluentinc/cp-kafka:3.0.0
