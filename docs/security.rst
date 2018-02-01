.. _security_with_docker :

Docker Security
===============

Confluent Platform supports cluster encryption and authentication, including a mix of authenticated and unauthenticated,
and encrypted and non-encrypted clients. Using security is optional. These security features are supported on the Confluent Platform Docker images:

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
  The images can be run with arbitrary user IDs. If there is a container engine vulnerability, arbitrary user IDs can prevent processes from escaping the container and gaining escalated permissions on the host node.


For details on the available security features in Confluent platform, see the :ref:`Confluent Platform Security
Overview Documentation <security>`.

For tutorials on using SSL in the Confluent Platform, see the documented tutorials on :ref:`SSL
<kafka_ssl_authentication>` and :ref:`SASL <kafka_sasl_auth>`.
