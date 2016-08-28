# docker-utils

##Overview

This is set of utilites which are used by the Confluent Docker images. It has two command line utilities which are used for testing if a Zookeeper or Kafka cluster is healthy and ready to accept client requests.


##How does it work ?

**zk-ready**

This command tries to connect to the cluster and waits for events which signify if the Zookeeper ensemble is ready.

| SASL Enabled ?   | Zookeeper Events   |
|---|---|
| No  | SyncConnected  |
| Yes  |SyncConnected, SaslAuthenticated  |

**kafka-ready**
This command sends a metadata query to the broker and verifies that expected no. of brokers are present.


##How to package / run ?

1. Create a jar with dependencies

		 mvn clean compile assembly:single

2. See `src/test/bin/cli-test.sh` for examples on running the commands.

## How to test ?

1. JUnit tests: mvn test
2. Shell test :

        cd docker-utils
        src/test/bin/cli-test.sh


## Client.properties

@@ -1,146 +0,0 @@
``bootstrap.servers``
  A list of host/port pairs to use for establishing the initial connection to the Kafka cluster. The client will make use of all servers irrespective of which servers are specified here for bootstrapping&mdash;this list only impacts the initial hosts used to discover the full set of servers. This list should be in the form <code>host1:port1,host2:port2,...</code>. Since these servers are just used for the initial connection to discover the full cluster membership (which may change dynamically), this list need not contain the full set of servers (you may want more than one, though, in case a server is down).

  * Type: list
  * Default:
  * Importance: high

``ssl.key.password``
  The password of the private key in the key store file. This is optional for client.

  * Type: password
  * Importance: high

``ssl.keystore.location``
  The location of the key store file. This is optional for client and can be used for two-way authentication for client.

  * Type: string
  * Importance: high

``ssl.keystore.password``
  The store password for the key store file.This is optional for client and only needed if ssl.keystore.location is configured.

  * Type: password
  * Importance: high

``ssl.truststore.location``
  The location of the trust store file.

  * Type: string
  * Importance: high

``ssl.truststore.password``
  The password for the trust store file.

  * Type: password
  * Importance: high

``sasl.kerberos.service.name``
  The Kerberos principal name that Kafka runs as. This can be defined either in Kafka's JAAS config or in Kafka's config.

  * Type: string
  * Importance: medium

``sasl.mechanism``
  SASL mechanism used for client connections. This may be any mechanism for which a security provider is available. GSSAPI is the default mechanism.

  * Type: string
  * Default: "GSSAPI"
  * Importance: medium

``security.protocol``
  Protocol used to communicate with brokers. Valid values are: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL.

  * Type: string
  * Default: "PLAINTEXT"
  * Importance: medium

``ssl.enabled.protocols``
  The list of protocols enabled for SSL connections.

  * Type: list
  * Default: [TLSv1.2, TLSv1.1, TLSv1]
  * Importance: medium

``ssl.keystore.type``
  The file format of the key store file. This is optional for client.

  * Type: string
  * Default: "JKS"
  * Importance: medium

``ssl.protocol``
  The SSL protocol used to generate the SSLContext. Default setting is TLS, which is fine for most cases. Allowed values in recent JVMs are TLS, TLSv1.1 and TLSv1.2. SSL, SSLv2 and SSLv3 may be supported in older JVMs, but their usage is discouraged due to known security vulnerabilities.

  * Type: string
  * Default: "TLS"
  * Importance: medium

``ssl.provider``
  The name of the security provider used for SSL connections. Default value is the default security provider of the JVM.

  * Type: string
  * Importance: medium

``ssl.truststore.type``
  The file format of the trust store file.

  * Type: string
  * Default: "JKS"
  * Importance: medium

``sasl.kerberos.kinit.cmd``
  Kerberos kinit command path.

  * Type: string
  * Default: "/usr/bin/kinit"
  * Importance: low

``sasl.kerberos.min.time.before.relogin``
  Login thread sleep time between refresh attempts.

  * Type: long
  * Default: 60000
  * Importance: low

``sasl.kerberos.ticket.renew.jitter``
  Percentage of random jitter added to the renewal time.

  * Type: double
  * Default: 0.05
  * Importance: low

``sasl.kerberos.ticket.renew.window.factor``
  Login thread will sleep until the specified window factor of time from last refresh to ticket's expiry has been reached, at which time it will try to renew the ticket.

  * Type: double
  * Default: 0.8
  * Importance: low

``ssl.cipher.suites``
  A list of cipher suites. This is a named combination of authentication, encryption, MAC and key exchange algorithm used to negotiate the security settings for a network connection using TLS or SSL network protocol.By default all the available cipher suites are supported.

  * Type: list
  * Importance: low

``ssl.endpoint.identification.algorithm``
  The endpoint identification algorithm to validate server hostname using server certificate.

  * Type: string
  * Importance: low

``ssl.keymanager.algorithm``
  The algorithm used by key manager factory for SSL connections. Default value is the key manager factory algorithm configured for the Java Virtual Machine.

  * Type: string
  * Default: "SunX509"
  * Importance: low

``ssl.trustmanager.algorithm``
  The algorithm used by trust manager factory for SSL connections. Default value is the trust manager factory algorithm configured for the Java Virtual Machine.

  * Type: string
  * Default: "PKIX"
  * Importance: low


