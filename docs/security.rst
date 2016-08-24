.. _security_with_docker :

Security
--------

TODO: add more quickstarts to the relevant quickstarts.

Using security is optional - non-secured clusters are supported, as well as a mix of authenticated, unauthenticated, encrypted
and non-encrypted clients.  The following security features are currently tested on the CP Docker images:

Test Matrix
~~~~~~~~~~~
.. csv-table::
   :header: "Component", "Tests"
   :widths: 20, 20

   "Zookeeper", "SASL, SSL"
   "Kafka", "SASL, SSL"
   "Confluent Control Center", "HTTPS"
   "Schema Registry", "HTTPS"
   "REST Proxy", "HTTPS"
   "Kafka Connect", "None"

For details on available security features in Confluent platform, please refer to the `Confluent Platform Security Overview Documentation <http://docs.confluent.io/3.0.0/kafka/security.html>`_.


Docker Security
~~~~~~~~~~~~~~~

1. Managing secrets

  When you enable security for the Confluent Platform, you need to pass secrets (credentials, certificates, keytabs, Kerberos config etc.) to the container. The images handle this by expecting the credentials to be available in the secrets directory. We specify a docker volume for secrets and expect the admin to map it to a directory on the host which contain the required secrets.  This solution is similar to `Kubernetes secret management <http://kubernetes.io/docs/user-guide/secrets/>`_.

  Note: We avoid passing secrets in environment variables as it is very hard to control access to environment variables. Docker inspect exposes the environment variables passed to the container, which can lead them to be exposed accidently in log aggregation and monitoring tools.

  For more details on the issue, please see: https://github.com/confluentinc/cp-docker-images/issues/3


2. Running containers with arbitrary User IDs

  The images can be run with arbitrary User IDs. This provides an additional layer security against processes achieves escalated permissions on the host node by escaping the container due to a container engine vulnerability.

  We followed the guidelines for security for Openshift to build this feature: https://docs.openshift.org/latest/creating_images/guidelines.html#openshift-origin-specific-guidelines.

.. toctree::
   :maxdepth: 3

   ssl