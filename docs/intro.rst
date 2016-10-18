.. _cpdocker_intro:

Introduction
============

This section provides an overview of Confluent's Docker images for the Confluent Platform.  We've included an overview of image design, a quickstart guide, advanced tutorials, and developer instructions for extending the images.  
The images are currently available on `DockerHub <https://hub.docker.com/u/confluentinc/>`_.  Alternatively, the source files for the images are `available on Github <https://github.com/confluentinc/cp-docker-images>`_ if you would prefer to extend and/or rebuild the images and upload them to your own DockerHub repository.

The images are currently only available for Confluent Platform 3.0.1.


Requirements
------------

Although the `quickstart guides <quickstart.html>`_ found in this section are meant to be self contained, we recommend first familiarizing yourself with Docker before you get started. 

The following are prerequisites for running the CP Docker images:

1. A working Docker environment (Don't use Docker for Mac - see below for details)
2. An understanding of how Docker host networks and bridge networks work (Highly Recommended)
3. Docker Version 1.11 or greater.  Previous versions are not currently tested.

Important Notes/Caveats
--------------

1. Not Supported for Docker for Mac
	
	We recommend not using these images with Docker for Mac at this time.  There are a couple of reasons for this:  first, Docker for Mac does not add hostname to ``/etc/hosts``.  Kafka needs the hostname to be resolveable.  Furthermore, the semantics for ``--net=host`` are not clear, so you are likely to encounter issues if using host networking on Docker for Mac.  For more details on these known issues, you can refer to the following links:

	- `Hostname Issue <https://forums.docker.com/t/docker-for-mac-does-not-add-docker-hostname-to-etc-hosts/8620/4>`_
	- Host networking on Docker for Mac: `link 1 <https://forums.docker.com/t/should-docker-run-net-host-work/14215>`_, `link 2 <https://forums.docker.com/t/net-host-does-not-work/17378/7>`_, `link 3 <https://forums.docker.com/t/explain-networking-known-limitations-explain-host/15205/4>`_

2. Mounted Volumes
	
	If you are using Kafka and Zookeeper, you should always `use mounted volumes <operations/external-volumes.html>`_ to persist data in the event that a container stops running or is restarted.  This is important when running a system like Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages.  

3. Bridge Networking vs. Host Networking

	Bridge networking is currently only supported on a single host.  For multiple hosts, you will need to use overlay networks which are not currently supported. It order to expose Kafka to clients outside of the bridge network, you need to find the container IP and put it in ``advertised.listeners``.  This can be difficult to achieve depending on how you're using the images.  Furthermore, it can add a network hop and may not be as performant as the host network, which shares the network stack.  In summary, host networking is the recommended option in the following cases:

		* Multi-host clusters without using Swarm/Kubernetes host network is the best approach
		* If you need clients to be able to access Kafka outside the bridge/overlay network

4. Always launch containers with ``Restart=always`` unless you are using a process manager.  
	 
5. These images are currently tested and shipped with `Azul Zulu OpenJDK <https://www.azul.com/products/zulu/>`_.  If you want to switch to Oracle Java, please refer to our instructions for extending the images

6. Adding Connectors to the Kafka Connect Image

	There are currently two ways to add new connectors to the Kafka Connect image.  

	* Build a new Docker image that has connector installed. You can follow the examples found in our documentation on `Extending Images <development.html#extending-the-docker-images>`_. You will need to make sure that the connector jars are on the classpath. 
	* Add the connector jars via volumes.  If you don't want to create a new Docker image, please see our documentation on `Configuring Kafka Connect with External Jars <operations/external-volumes.html>`_ to configure the `cp-kafka-connect` container with external jars.
	 
7. Untested Features
	
	The following features/conditions are not currently tested:

		* Kafka Connect with Security Enabled
		* Control Center with Security Enabled 
		* Schema Registry SSL
		* The images are not currently tested on Docker Swarm.

License
-------

The Confluent Platform Docker Images are available as open source software under the Apache License v2.0 license.  For more information on the licenses for each of the individual Confluent Platform components packaged in the images, please refer to the `respective Confluent Platform documentation for each component <http://docs.confluent.io/current/platform.html>`_.  
