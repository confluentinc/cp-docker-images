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

2. Run the jar.

		java -jar target/docker-utils-1.0.0-SNAPSHOT-jar-with-dependencies.jar zk-ready localhost:2181 30000 false &&  echo "READY" || echo "NOTREADY"
	    java -jar target/docker-utils-1.0.0-SNAPSHOT-jar-with-dependencies.jar kafka-ready localhost:2181/ssl client.props 1 30000 &&  echo "READY" || echo "NOTREADY"

## How to test ?

1. JUnit tests: mvn test
2. Shell test :

        cd docker-utils
        test/bin/cli-test.sh


## Client.properties 
See client.properties.html