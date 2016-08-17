The bootup process
------------------

The entrypoint ``/etc/confluent/docker/run`` runs three executable in
the ``/etc/confluent/docker`` in the following sequence:

``/etc/confluent/docker/configure``

``/etc/confluent/docker/ensure``

``/etc/confluent/docker/launch``

Configuration
~~~~~~~~~~~~~

The ``configure`` script does all the configuration. This includes :

-  Creating all configuration files and copying them to their proper
   location
-  It is also responsible for handling service discovery if required.

Preflight checks
~~~~~~~~~~~~~~~~

The ``ensure`` scripts makes sure that all the prerequisites for
launching the service are in place. This includes:

-  Ensure the configuration files are present and readable.
-  Ensure that you can write/read to the data directory. The directories
   need to be world writable.
-  Ensuring supporting services are in READY state. For example, ensure
   that ZK is ready before launching Kafka broker.
-  Ensure supporting systems are configured properly. For example, make
   sure all topics required for C3 are created with proper replication,
   security and partition settings.

Launching the process
~~~~~~~~~~~~~~~~~~~~~

The ``launch`` script runs the actual process. The script should ensure
that :

-  The process is run properly. You need to do ``exec`` (Note to self:
   Why was this needed again?)
-  Log to stdout

Guidelines for the scripts
--------------------------

-  Make it executable
-  Fail fast
-  Fail with good error messages
-  Return 0 if success, 1 if fail
