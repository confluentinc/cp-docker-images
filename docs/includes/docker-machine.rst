Create a VirtualBox Instance
----------------------------

Create and configure the Docker Machine on VirtualBox.

.. important:: This step is only for Mac and Windows users who are not using Docker for Mac or Docker for Windows.

#. Create a `VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_ instance running a Docker container named ``confluent`` with 6 GB of memory.

   .. codewithvars:: bash

    docker-machine create --driver virtualbox --virtualbox-memory 6000 confluent

#. Configure your terminal window to attach it to your new Docker Machine:

   .. codewithvars:: bash

     docker-machine env confluent


