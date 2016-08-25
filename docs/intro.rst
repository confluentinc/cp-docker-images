.. _cpdocker_intro:

Introduction
============

This section provides an overview of Confluent's Docker images for the Confluent Platform.  It includes an overview image design, quickstart tutorials, and developer instructions for extending the images.  

The images are currently available on `DockerHub <https://hub.docker.com/u/confluentinc/>`_.  Alternatively, the source files for the images are `available on Github <https://github.com/confluentinc/cp-docker-images>`_ if you would prefer to extend and/or rebuild the images and upload them to your own DockerHub repository.

The images are currently only available for Confluent Platform 3.0.1.

Requirements
------------

Although the `quickstart guides <quickstart.html>`_ found in this section are meant to be self contained, we recommend first familiarizing yourself with Docker before you get started. 

The following are prerequisites for running the CP Docker images:

1. A working Docker environment
2. An understanding of how Docker host networks and bridge networks work (Highly Recommended)
3. Docker Version 1.11 or greater.  Previous versions are not currently tested.

Important Caveats
--------------

1. Mounted Volumes:
	
	If you are using Kafka and Zookeeper, you should always `use mounted volumes <operations/external-volumes.html>`_ to persist data in the event that a container stops running or is restarted.  This is important when running a system like Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages.  

2. Bridge Networking vs. Host Networking:

	Bridge networking is currently only supported on a single host.  For multiple hosts, you will need to use overlay networks which are not currently supported. It order to expose Kafka to clients outside of the bridge network, you need to find the container IP and put it in ``advertised.listeners``.  This can be difficult to achieve depending on how you're using the images.  Furthermore, it can add a network hop and may not be as performant as the host network, which shares the network stack.  In summary, host networking is the recommended option in the following cases:

		* Multi-host clusters without using Swarm/Kubernetes host network is the best approach
		* If you need clients to be able to access Kafka outside the bridge/overlay network

3. Always launch containers with ``Restart=always`` unless you are using a process manager.  
	 
4. These images are currently tested and shipped with `Azul Zulu OpenJDK <https://www.azul.com/products/zulu/>`_.  If you want to switch to Oracle Java, please refer to our instructions for extending the images
	 
5. Untested Features
	
	The following features/conditions are not currently tested:

		* Kafka Connect with Security Enabled
		* Control Center with Security Enabled 
		* Schema Registry SSL
		* The images are not currently tested on Docker Swarm.

License
-------

The Confluent Platform Docker Images are available as open source software under the Apache License v2.0 license.  For more information on the licenses for each of the individual Confluent Platform components packaged in the images, please refer to the `respective Confluent Platform documentation for each component <http://docs.confluent.io/current/platform.html>`_.  



