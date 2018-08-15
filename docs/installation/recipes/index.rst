.. _tutorials_overview:

Docker Installation Recipes
===========================

This section provides installation recipes for using specific |cp| features on Docker.

.. toctree::
   :maxdepth: 1
   :hidden:

   single-node-client
   clustered-deployment
   clustered-deployment-ssl
   clustered-deployment-sasl
   connect-avro-jdbc
   automatic-data-balancing
   replicator


You should consider the following before using the Docker images.

Persistent Data (Mounted Volumes)
    When deploying the Kafka and |zk| images, you should always use :ref:`mounted volumes <external_volumes>`
    for the file systems those images use for their persistent data.  This ensures that the containers will retain their
    proper state when stopped and restarted.  The other images maintain their state directly in Kafka topics, so mounted
    volumes are not usually required for those containers.

Bridge Networking vs. Host Networking
    Bridge networking is currently only supported on a single host.  For multiple hosts, you must use overlay networks which
    are not currently supported. To expose Kafka to clients outside of the bridge network, you must find the container
    IP and put it in ``advertised.listeners``.  This can be difficult to achieve depending on how you're using the images.
    Furthermore, it can add a network hop and may not be as performant as the host network, which shares the network stack.
    Host networking is the recommended option in the following cases:

    * Multi-host clusters without using Swarm/Kubernetes host network is the best approach
    * If you need clients to be able to access Kafka outside the bridge/overlay network

Adding Connectors to the Kafka Connect Image
    Here are the methods to add new connectors to the Kafka Connect image.

    * Build a new Docker image that has the connector installed. You can follow the examples found in
      :ref:`Extending Images <extending_images>`. You must make sure that the connector
      JARs are on the CLASSPATH for the Connect service (the default location of ``/usr/share/java/kafka-connect-*`` is the
      recommended location).
    * Add the connector JARs via volumes.  If you don't want to create a new Docker image, please see our documentation
      on :ref:`Configuring Kafka Connect with External Jars <external_volumes>` to configure the ``cp-kafka-connect``
      container with external JARs.

Supported Java
    The Confluent Docker images are tested and shipped with `Azul Zulu OpenJDK <https://www.azul.com/products/zulu/>`_.
    Other JDK's (including Oracle Java) are supported, but you must extend the images yourself to implement that change.

Untested Features
    The images are not currently tested on Docker Swarm.

Installation Recipes
    .. toctree::
       :maxdepth: 1

       single-node-client
       clustered-deployment
       clustered-deployment-ssl
       clustered-deployment-sasl
       connect-avro-jdbc
       automatic-data-balancing
       replicator