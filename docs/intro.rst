.. _cpdocker_intro:

Introduction
============

This section provides an overview of Confluent's Docker images for the Confluent Platform.  It includes an overview image design, quickstart tutorials, and developer instructions for extending the images.  

The images are currently available on `DockerHub <https://hub.docker.com/u/confluentinc/>`_ in the ``confluentinc`` repository.  Alternatively, the source files for the images are `available on Github <https://github.com/confluentinc/cp-docker-images>`_ if you would prefer to extend and/or rebuild the images and upload them to your own DockerHub repository.

The images are only currently available for Confluent Platform 3.0.1.

Requirements
------------

Although the `quickstart guides <quickstart.html>`_ found in this section are meant to be self contained, we recommend first familiarizing yourself with Docker before you get started. 

The following are prerequisites for running the CP Docker images:

1. A working Docker environment
2. An understanding of how Docker host networks and bridge networks work (Highly Recommended)
3. Docker Version 1.11 or greater.  Previous versions are not currently tested.

License
-------

The Confluent Platform Docker Images are available as open source software under the Apache License v2.0 license.  For more information on the licenses for each of the individual Confluent Platform components packaged in the images, please refer to the `respective Confluent Platform documentation for each component <http://docs.confluent.io/current/platform.html>`_.  Source code for these Docker images is available at .



