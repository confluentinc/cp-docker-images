.. _security_with_docker :

Security Overview
=================

Using security is optional - non-secured clusters are supported, as well as a mix of authenticated, unauthenticated, encrypted and non-encrypted clients.  The following security features are currently supported on the Confluent Platform Docker images:

.. csv-table::
   :header: "Component", "Tests"
   :widths: 20, 20

   "Zookeeper", "SASL, SSL"
   "Kafka", "SASL, SSL"
   "Confluent Control Center", "HTTPS"
   "Schema Registry", "HTTPS"
   "REST Proxy", "HTTPS"
   "Kafka Connect", "None"

For details on available security features in Confluent platform, please refer to the `Confluent Platform Security Overview Documentation <http://docs.confluent.io/3.0.1/kafka/security.html>`_.

Docker Security
~~~~~~~~~~~~~~~

1. Managing secrets

  When you enable security for the Confluent Platform, you need to pass secrets (credentials, certificates, keytabs, Kerberos config etc.) to the container. The images handle this by expecting the credentials to be available in the secrets directory. We specify a docker volume for secrets and expect the admin to map it to a directory on the host which contain the required secrets.

2. Running containers with arbitrary User IDs

  The images can be run with arbitrary User IDs. This provides an additional security layer against processes achieving escalated permissions on the host node by escaping the container if there is a container engine vulnerability.
