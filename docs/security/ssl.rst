Encryption and Authentication Using SSL
---------------------------------------

To enable encryption, you need to perform the following steps on each broker / logical client in the cluster:

1. Install an X.509 certificate.
2. Configure the broker to enable SSL for client-broker communication and for inter-broker communication.
3. Reboot the broker.

Installing Certificates
~~~~~~~~~~~~~~~~~~~~~~~

The certificates for each node should be signed by a certificate authority (CA) that is trusted by every node in the cluster. You can use a third-party CA, your organization’s existing CA, or set up a certificate authority specifically for signing node certificates.

When a client connects to a broker using SSL/TLS, the broker presents its certificate to the client and proves that it owns the private key linked with the certificate. The client then determines if the node’s certificate is valid, trusted, and matches the hostname or IP address it is trying to connect to.

A broker acts as a client when connecting to other brokers in the cluster, so every broker must trust all of the other brokers in the cluster.

**Note**

While it is technically possible to use self-signed certificates, we strongly recommend using certificates signed by a CA to establish trust between nodes. Self-signed certificates must be trusted individually, which means that each broker must have every other broker's certificate installed. If you add a broker to the cluster, you have to install the new broker's self-signed certificate on all of the existing nodes and restart them. When you use CA-signed certificates, the existing brokers just need to trust the CA used to sign the new broker's certificate. (You should use the same CA to sign all of your broker certificates.)

To install a signed certificate, you need to:

1. Create a keystore and generate a certificate for the broker.
2. Create a certificate signing request (CSR).
3. Send the certificate to your CA for signing.
4. Add the signed certificate to the node’s keystore.


1. Creating a Keystore and Generating a Certificate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a keystore and generate a broker certificate:

1. Create a broker truststore and import the CA certificate(s) you want to trust with Java Keytool. This configures the broker to trust certificates signed by the CA. 

	For example, the following command imports the CA certificate cacert.pem into broker01.truststore.jks. If the specified truststore doesn’t exist, it is created.
	
	.. sourcecode:: bash
		
		$ keytool -keystore broker01.truststore.jks -alias CARoot -import -file cacert.pem
			
	The Java keystore file (.jks) securely stores certificates for the broker. The CA cert must be a PEM encoded certificate.

	When you create a truststore, you are prompted to set a password. This password protects the integrity of the truststore. You need to provide it whenever you interact with the truststore.

	**Important** When the CA certificate expires, you must update the node’s keystore with the new CA certificate.

	To create your own CA, follow the steps in [Setting Up a Certificate Authority](https://www.elastic.co/guide/en/shield/current/certificate-authority.html)

2. Generate a private key and certificate for the node with Java Keytool. For example, the following command creates a key and certificate for broker01:

	.. sourcecode:: bash

		$ keytool -genkey \
			 -alias broker01 \
			 -keystore broker01.keystore.jks \
			 -keyalg RSA \
			 -keysize 2048 \
			 -validity 712 
	
	
	The Keytool will prompt you for the information needed to populate the brokers distinguished name that’s stored in the certificate. 

	.. sourcecode:: bash

		What is your first and last name?
		  [Unknown]:  broker1.test.confluent.io
		What is the name of your organizational unit?
		  [Unknown]:  test
		What is the name of your organization?
		  [Unknown]:  confluent
		What is the name of your City or Locality?
		  [Unknown]:  PaloAlto
		What is the name of your State or Province?
		  [Unknown]:  California
		What is the two-letter country code for this unit?
		  [Unknown]:  US
		Is CN=broker1.test.confluent.io, OU=teset, O=confluent, L=PaloAlto, S=Californoa, C=US" correct?
		  [no]:  yes
		
		Enter key password for <broker1.test.confluent.io>
		    (RETURN if same as keystore password):
	
	If you don’t specify a password for the certificate, the keystore password is used.

	This command creates an RSA private key with a key size of 2048 bits and a public certificate that is valid for 712 days. The key and certificate are stored in the broker.keystore.jks keystore.

	You will need to ensure that common name (CN) matches exactly with the fully qualified domain name (FQDN) of the server. 

	**Important**

	Specifying the Broker Identity
	
	With SSL/TLS is enabled, when client connects to a broker, the client verifies the identity of the broker by checking the identity information specified in broker's certificate. This means that you must include node identity information when you create a node’s certificate.

	The recommended way to specify the broker identity when creating a certificate is to set CN field to FQDN of the server. The CN field specifies the broker's identity using a DNS name. The client compares the CN with the DNS domain name to ensure that it is indeed connecting to the desired server, not a malicious one.

	If you use a commercial CA, the DNS names and IP addresses used to identify a node must be publicly resolvable. Internal DNS names and private IP addresses are not accepted due to security concerns.

	If you need to use private DNS names and IP addresses, using an internal CA is the most secure option. It enables you to specify node identities and ensure node identities are verified when nodes connect.
  
	**Important**
	
	Extended Key Usage (NOT SUPPORTED BY KAFKA. See: https://confluent.zendesk.com/agent/tickets/214)
	
	The Extended Key Usage attribute in a certificate is used to indicate the purpose of the key. Extended Key Usage attribute is not supported by Kafka. By default keytool does not set this attribute in the certificate. If you are generating your certificates with another tool, please ensure that extended attributes are not set.

2. Creating a Certificate Signing Request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A node’s certificate needs to be signed by a trusted CA for the certificate to be trusted. To get a certificate signed, you need to create a certificate signing request (CSR) and send it to your CA.

To create a CSR with Java Keytool, use the `keytool -certreq` command. You specify the same alias, keystore, key algorithm, and DNS names and IP addresses that you used when you created the broker certificate. Specify where you want to store the CSR with the -file option.

	.. sourcecode:: bash
		
		$ keytool -certreq -alias broker01 -keystore broker01.keystore.jks -file broker01.csr -keyalg rsa 

3. Send the Signing Request
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To get a signed certificate, send the generated CSR file to your CA. The CA will sign it and send you the signed version of the certificate.

Note: If you are running your own CA, see [Signing CSRs for signing](https://www.elastic.co/guide/en/shield/current/certificate-authority.html#sign-csr).
 

4. Install the Signed Certificate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install the signed certificate, use keytool -importcert to add it to the node’s keystore. You specify the same alias and keystore that you used when you created the node certificate. You will also need to add the CA certificate.

	.. sourcecode:: bash

		$ keytool -keystore broker01.keystore.jks -alias CARoot -import -file cacert.pem
		$ keytool -import -keystore broker01.keystore.jks -file broker01-signed.crt -alias broker01


**Note**
	
  If you attempt to import a PEM-encoded certificate that contains extra text headers, you might get the error: 	java.security.cert.CertificateParsingException: invalid DER-encoded certificate data. Use the following openssl command to remove the extra headers and then use keytool to import the certificate.

  .. sourcecode:: bash
		$ openssl x509 -in broker01-signed.crt -out broker01-signed-noheaders.crt


Enabling SSL in the Broker Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have added the signed certificate to the broker's keystore, you need to modify the broker configuration to enable SSL. See [Enabling SSL on brokers](http://docs.confluent.io/3.0.0/kafka/ssl.html#configuring-kafka-brokers) 