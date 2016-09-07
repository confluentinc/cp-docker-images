.. _operations_overview :

Operations
==========

In this section, we provide a closer look at how to run a Confluent Platform cluster on Docker.  If you are looking for a simple tutorial, you should refer instead to the `quickstart guide <quickstart.html>`_.

We will cover the following topics:

- Montoring: How to set up monitoring with JMX, as well as recommendations for extending the images to use other monitoring solutions.
- Logging: Using log4j in a Docker setup.
- Networking: Bridge and host networking (including caveats for each)
- Mounting External Volumes: This is important when running Kafka Brokers and ZooKeeper on Docker, as they require a persistent filesystem.

.. toctree::
   :maxdepth: 3

   monitoring
   logging
   external-volumes
