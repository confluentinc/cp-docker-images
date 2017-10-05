.. _cpdocker_intro:

Introduction
============

This section provides an overview of Confluent's Docker images for the Confluent Platform.  We've included an overview of image design, a quickstart guide, advanced tutorials, and developer instructions for extending the images.
The images are currently available on `DockerHub <https://hub.docker.com/u/confluentinc/>`_.  Alternatively, the source files for the images are `available on Github <https://github.com/confluentinc/cp-docker-images>`_ if you would prefer to extend and/or rebuild the images and upload them to your own DockerHub repository.

The images are available for Confluent Platform 3.0.1 and greater.

Choosing the Right Images
-------------------------

Images are available on DockerHub for each component of the Confluent Platform.  If you are not yet familiar with the Confluent Platform, we suggest starting with this `overview <http://docs.confluent.io/current/platform.html>`_.

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
| Kafka Connect    | cp-kafka-connect             | Enterprise   | - confluent-kafka-connect-jdbc          |
|                  |                              |              | - confluent-kafka-connect-hdfs          |
|                  |                              |              | - confluent-schema-registry             |
|                  |                              |              | - confluent-control-center              |
|                  |                              |              | - confluent-kafka-connect-elasticsearch |
+------------------+------------------------------+--------------+-----------------------------------------+
| Schema Registry  | cp-schema-registry           | Open Source  | - confluent-schema-registry             |
+------------------+------------------------------+--------------+-----------------------------------------+
| REST Proxy       | cp-kafka-rest                | Open Source  | - confluent-kafka-rest                  |
+------------------+------------------------------+--------------+-----------------------------------------+

Note: The Kafka Connect image is labeled as "Enterprise" simply because it contains the Confluent Control Center package.  That package enables the deployed connectors to collect the metrics visualized in Confluent Control Center.   No explicit license is required when using the Kafka Connect image on its own.


Requirements
------------

Although the `quickstart guides <quickstart.html>`_ found in this section are meant to be self contained, we recommend familiarizing yourself with Docker before you get started.

The following are prerequisites for running the CP Docker images:

1. Docker Version 1.11 or greater.  Previous versions have not been tested.
2. A working Docker environment (Docker for Mac is not recommended - see below)
3. An understanding of how Docker host networks and bridge networks work (Highly Recommended)

Important Notes/Caveats
-----------------------

1. Docker for Mac

	We do not recommend using these images with Docker for Mac at this time.  The primary reason is that Docker for Mac does not update the local /etc/hosts file with the hostnames of the deployed containers.   This makes it difficult to access the containerized cluster with client applications running directly on the Mac.  Additionally, the semantics of ``--net=host`` are not clear, so deploying containers with host networking on Docker for Mac is not reliable.  More details on these issues can be found at:

	- `Hostname Issue <https://forums.docker.com/t/docker-for-mac-does-not-add-docker-hostname-to-etc-hosts/8620/4>`_
	- Host networking on Docker for Mac: `link 1 <https://forums.docker.com/t/should-docker-run-net-host-work/14215>`_, `link 2 <https://forums.docker.com/t/net-host-does-not-work/17378/7>`_, `link 3 <https://forums.docker.com/t/explain-networking-known-limitations-explain-host/15205/4>`_

2. Persistent Data (Mounted Volumes)

	When deploying the Kafka and ZooKeeper images, you should always use `mounted volumes <operations/external-volumes.html>`_ for the file systems those images use for their persistent data.  This ensures that the containers will retain their proper state when stopped and restarted.  The other images maintain their state directly in Kafka topics, so mounted volumes are not usually required for those containers.

3. Bridge Networking vs. Host Networking

	Bridge networking is currently only supported on a single host.  For multiple hosts, you will need to use overlay networks which are not currently supported. It order to expose Kafka to clients outside of the bridge network, you need to find the container IP and put it in ``advertised.listeners``.  This can be difficult to achieve depending on how you're using the images.  Furthermore, it can add a network hop and may not be as performant as the host network, which shares the network stack.  In summary, host networking is the recommended option in the following cases:

		* Multi-host clusters without using Swarm/Kubernetes host network is the best approach
		* If you need clients to be able to access Kafka outside the bridge/overlay network

4. Launch Settings

    Docker containers should be launched with ``Restart=always`` unless you are using a process manager.   This ensures that intermittent failures in the Docker environment do not result in unnecessary failures of the Confluent services.

5. Adding Connectors to the Kafka Connect Image

	There are currently two ways to add new connectors to the Kafka Connect image.

	* Build a new Docker image that has the connector installed. You can follow the examples found in `Extending Images <development.html#extending-the-docker-images>`_. You will need to make sure that the connector jars are on the CLASSPATH for the Connect service (the default location of /usr/share/java/kafka-connect-* is the recommended location).
	* Add the connector jars via volumes.  If you don't want to create a new Docker image, please see our documentation on `Configuring Kafka Connect with External Jars <operations/external-volumes.html>`_ to configure the `cp-kafka-connect` container with external jars.

6. Included Java

    The Confluent Docker images are tested and shipped with `Azul Zulu OpenJDK <https://www.azul.com/products/zulu/>`_.  Other JDK's (including Oracle Java) are supported, but you must extend the images yourself to implement that change. 

7. Untested Features

	The following features/environments are not currently tested:

		* Schema Registry SSL
		* Kafka Connect with Security Enabled
		* Confluent Control Center with Security Enabled
		* The images are not currently tested on Docker Swarm.

License
-------

The Confluent Platform Docker Images are available as open source software under the Apache License v2.0 license.  License details for the individual Confluent Platform components packaged in the images are available with the top-level `platform documentation <http://docs.confluent.io/current/platform.html>`_.
