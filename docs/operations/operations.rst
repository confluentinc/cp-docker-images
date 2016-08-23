.. _operations_overview :

Operations
-----------

In this section, we provide a closer look at how to run a Confluent Platform cluster on Docker.  If you are looking for a simple tutorial, you should refer instead to the `quickstart guide <quikstart.html>`_.

We will cover the following topics:

- Clustered Environemnts: We'll discuss how to set up and run a CP deployment in a clustered environment.  This is in contrast to the quickstart guide, which only looked at a single-node deployment. 
- Montoring Your Cluster: We will provide an overview of how to set up monitoring with JMX, as well as recommendations for extending the images to use other monitoring solutions, if required.
- Logging
- Networking: We'll provide some information on bridged and host networking (including caveats for each)
- Mounting External Volumes: This is important when running a system like Kafka on Docker, as it relies heavily on the filesystem for storing and caching messages.  

.. toctree::
   :maxdepth: 3

   jmx
   logging
   external-volumes