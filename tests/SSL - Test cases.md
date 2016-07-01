SSL testcases
===

###Notes
- Thanks Alex for explaining all this to me !
- Keystore is where the component (broker, client) keeps their own private key and certificate.
- Truststore contains the certificate for the trusted parties (i.e it will talk only to parties whose certs are in the truststore)

- SSL authentication can be based on
	- CA certificates: which means that anyone with certs signed by the CA (which has a cert in the truststore) is trusted.
	- Certificates: which means anyone who has certs in the truststore is trusted.

- To prevent MITM attacks, use CA certificates even if SSL authentication is not desired 	 

## Generating the certs and keys

1. Generate CA certs

		openssl req -new -x509 -keyout snakeoil-ca-1.key -out snakeoil-ca-1.crt -days 365 -subj '/CN=ca1.test.confluent.io/OU=TEST/O=CONFLUENT/L=PaloAlto/S=Ca/C=US' -passin pass:confluent -passout pass:confluent
		openssl req -new -x509 -keyout snakeoil-ca-2.key -out snakeoil-ca-2.crt -days 365 -subj '/CN=ca1.test.confluent.io/OU=TEST/O=CONFLUENT/L=PaloAlto/S=Ca/C=US' -passin pass:confluent -passout pass:confluent

2. Generate Broker keys and certs

	Generate keystore

		openssl req -new -x509 -keyout snakeoil-ca-1.key -out snakeoil-ca-1.crt -days 365 -subj '/CN=ca1.test.confluent.io/OU=TEST/O=CONFLUENT/L=PaloAlto/S=Ca/C=US' -passin pass:confluent -passout pass:confluent

	Export the broker cert from the keystore

		keytool -keystore kafka.broker1.keystore.jks -alias broker1 -certreq -file broker1.crt

	Sign the cert with CA cert

		openssl x509 -req -CA snakeoil-ca-1.crt -CAkey snakeoil-ca-1.key -in broker1.crt -out broker1-ca1-signed.crt -days 9999 -CAcreateserial -passin pass:confluent

3. Add back to broker keystore
		
		keytool -keystore kafka.broker1.keystore.jks -alias CARoot -import -file snakeoil-ca-1.cr
		keytool -keystore kafka.broker1.keystore.jks -alias broker1 -import -file broker1-ca1-signed.crt

4. Add CA cert to broker truststore

		keytool -keystore kafka.broker1.truststore.jks -alias CARoot -import -file snakeoil-ca-1.crt


##1. Broker and client share the same CA

###Given

**CA**

- CA1 : CA1-cert

**Brokers**

- B1: B1-private-key, B1-cert(signed by CA1)
- B2: B2-private-key, B2-cert(signed by CA1)

**Clients**  

- C1: C1-private-key, C1-cert(signed by CA1)
- C2: C2-private-key, C2-cert(signed by CA1)



###Case 1: CA based authentication

**Broker 1**

- Keystore : B1-private-key, B1-cert
- Truststore : CA1-cert

**Broker 2**

- Keystore : B2-private-key, B2-cert
- Truststore : CA1-cert

**Client 1**

- Keystore : C1-private-key, C1-cert
- Truststore: CA1-cert

###Case 2: Cert based authentication

**Broker 1**

- Keystore : B1-private-key, B1-cert
- Truststore : B2-cert, C1-cert, C2-cert

**Broker 2**

- Keystore : B2-private-key, B2-cert
- Truststore : B1-cert, C1-cert, C2-cert

**Client 1**

- Keystore : C1-private-key, C1-cert
- Truststore: B1-cert, B2-cert


##2. Broker and client have different CA

###Given

**CA**

- CA1 : CA1-cert
- CA2 : CA2-cert

**Brokers**

- B1: B1-private-key, B1-cert(signed by CA1)
- B2: B2-private-key, B2-cert(signed by CA1)

**Clients**  

- C1: C1-private-key, C1-cert(signed by CA2)
- C2: C2-private-key, C2-cert(signed by CA2)



###Case 1: CA based authentication

**Broker 1**

- Keystore : B1-private-key, B1-cert
- Truststore : CA1-cert, CA2-cert

**Broker 2**

- Keystore : B2-private-key, B2-cert
- Truststore : CA1-cert, CA2-cert

**Client 1**

- Keystore : C1-private-key, C1-cert
- Truststore: CA1-cert

###Case 2: Cert based authentication

**Broker 1**

- Keystore : B1-private-key, B1-cert
- Truststore : CA1-cert, C1-cert, C2-cert

**Broker 2**

- Keystore : B2-private-key, B2-cert
- Truststore : CA1-cert, C1-cert, C2-cert

**Client 1**

- Keystore : C1-private-key, C1-cert
- Truststore: CA1-cert
