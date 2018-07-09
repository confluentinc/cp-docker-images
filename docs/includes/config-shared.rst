.. shared config file

Also notice that ``KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR`` is set to ``1``.  This is required when you are running with
a single-node cluster.  If you have three or more nodes, you can use the default.

.. config parameters

""""""""""""""""""""""""""""""
``KAFKA_ADVERTISED_LISTENERS``
""""""""""""""""""""""""""""""
Listeners to publish to |zk| for clients to use. In a Docker environment, your clients must be able to connect to Kafka
and other services.  The advertised listeners configuration setting describes how the host name that is advertised and can
be reached by the client.

