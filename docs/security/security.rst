.. _security_with_docker :

Docker Security
===============

Using security is optional. Confluent Platform supports non-secured clusters and a mix of authenticated, unauthenticated,
encrypted, and non-encrypted clients.  These security features are supported on the Confluent Platform Docker images:

.. csv-table::
   :header: "Component", "Tests"
   :widths: 20, 20

   "Confluent Control Center", "HTTPS"
   "Kafka Connect", "None"
   "Kafka", "SASL, SSL"
   "REST Proxy", "HTTPS"
   "Schema Registry", "HTTPS"
   "ZooKeeper", "SASL"


Managing secrets
  When you enable security for the Confluent Platform, you must pass secrets (e.g., credentials, certificates, keytabs,
  Kerberos config etc.) to the container. The images handle this by expecting the credentials to be available in the
  secrets directory. The containers specify a Docker volume for secrets and expect the admin to map it to a directory on the host
  which contains the required secrets.

Running containers with arbitrary user IDs
  The images can be run with arbitrary user IDs. This provides an additional security layer against processes achieving
  escalated permissions on the host node by escaping the container if there is a container engine vulnerability.


For details on the available security features in Confluent platform, see the `Confluent Platform Security
Overview Documentation <http://docs.confluent.io/current/kafka/security.html>`_.

For a tutorials on using SSL in the Confluent Platform, see the documented tutorials on `SSL
<http://docs.confluent.io/current/kafka/ssl.html>`_ and `SASL <http://docs.confluent.io/current/kafka/sasl.html>`_.