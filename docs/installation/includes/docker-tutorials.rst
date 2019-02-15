.. note

.. note:: In this tutorial, Kafka and |zk| are configured to store data locally in the Docker containers. For production
          deployments (or generally whenever you care about not losing data), you should use mounted volumes for persisting
          data in the event that a container stops running or is restarted.  This is important when running a system like
          Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages. For an example of how to add
          mounted volumes to the host machine, see the :ref:`documentation on Docker external volumes <external_volumes>`.
.. install-run
Installing and Running Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this tutorial, Docker is run using the Docker client.  If you are interested in information on using Docker Compose
to run the images, :ref:`skip to the bottom of this guide <clustered_quickstart_compose_ssl>`.

To get started, you'll need to first `install Docker and get it running <https://docs.docker.com/engine/installation/>`_.
The |cp| Docker Images require Docker version 1.11 or greater.

.. setting-up-3-node
Docker Client: Setting Up a Three Node Kafka Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're running on Windows or Mac OS X, you'll need to use `Docker Machine <https://docs.docker.com/machine/install-machine/>`_
to start the Docker host.  Docker runs natively on Linux, so the Docker host will be your local machine if you go that route.
If you are running on Mac or Windows, be sure to allocate at least 4 GB of ram to the Docker Machine.

Now that you have all of the Docker dependencies installed, you can create a Docker machine and begin starting up |cp|.

.. note:: In the following steps, each Docker container is run in detached mode and you are shown how to access to the
          logs for a running container. You can also run the containers in the foreground by replacing the ``-d`` flags
          with ``-it``.

#. Create and configure the Docker machine.

   .. codewithvars:: bash

    docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent

   Next, configure your terminal window to attach it to your new Docker Machine:

   .. codewithvars:: bash

    eval $(docker-machine env confluent)

#. Clone the git repository:

   .. codewithvars:: bash

    git clone https://github.com/confluentinc/cp-docker-images
    cd cp-docker-images

