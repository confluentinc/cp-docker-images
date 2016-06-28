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
