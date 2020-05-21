.. _clustered_deployment_sasl:

Clustered Deployment Using SASL and SSL
----------------------------------------

This tutorial runs a secure three-node Kafka cluster and |zk| ensemble with SASL.  By the end of this tutorial, you will have successfully installed and run a simple deployment with SSL and SASL security enabled on Docker.  If you're looking for a simpler tutorial, please :ref:`refer to the quick start guide <docker_quickstart>`, which is limited to a single node Kafka cluster.

.. include:: includes/docker-tutorials.rst
    :start-line: 2
    :end-line: 19


.. _docker-client-setup-3-node-sasl:

.. include:: includes/docker-tutorials.rst
    :start-line: 21

#. Generate Credentials

   You must generate CA certificates (or use yours if you already have one) and then generate a keystore and truststore
   for brokers and clients. You can use the ``create-certs.sh`` script in ``examples/kafka-cluster-ssl/secrets`` to generate
   them. For production, use `these scripts <https://github.com/confluentinc/confluent-platform-security-tools>`_ for
   generating certificates.

   For this example, we will use the ``create-certs.sh`` available in the ``examples/kafka-cluster-sasl/secrets`` directory in cp-docker-images. See "security" section for more details on security. Make sure that you have OpenSSL and JDK installed.

   .. sourcecode:: bash

    cd $(pwd)/examples/kafka-cluster-sasl/secrets
    ./create-certs.sh
    (Type yes for all "Trust this certificate? [no]:" prompts.)
    cd -

   Set the environment variable for secrets directory. We will use this later in our commands. Make sure you are in the ``cp-docker-images`` directory.

   .. sourcecode:: bash

        export KAFKA_SASL_SECRETS_DIR=$(pwd)/examples/kafka-cluster-sasl/secrets

   To configure SASL, all your nodes will need to have a proper hostname. It is not advisable to use ``localhost`` as the hostname.

   You must create an entry in ``/etc/hosts`` with hostname ``quickstart.confluent.io`` that points to ``eth0`` IP. In Linux, run the below commands on the Linux host. If running Docker Machine (eg for Mac or Windows), you will need to SSH into the VM and run the below commands as root. You can SSH into the Docker Machine VM by running ``docker-machine ssh confluent``.

   .. sourcecode:: bash

    export ETH0_IP=$(ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')

    echo ${ETH0_IP} quickstart.confluent.io >> /etc/hosts

#. Build and run the kerberos image

   .. sourcecode:: bash

    cd tests/images/kerberos
    docker build -t confluentinc/cp-kerberos:4.1.4 .

    docker run -d \
      --name=kerberos \
      --net=host \
      -v ${KAFKA_SASL_SECRETS_DIR}:/tmp/keytab \
      -v /dev/urandom:/dev/random \
      confluentinc/cp-kerberos:4.1.4

#. Create the principals and keytabs.

   .. sourcecode:: bash

    for principal in zookeeper1 zookeeper2 zookeeper3
    do
      docker exec -it kerberos kadmin.local -q "addprinc -randkey zookeeper/quickstart.confluent.io@TEST.CONFLUENT.IO"
      docker exec -it kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab zookeeper/quickstart.confluent.io@TEST.CONFLUENT.IO"
    done

   .. sourcecode:: bash

    for principal in zkclient1 zkclient2 zkclient3
    do
      docker exec -it kerberos kadmin.local -q "addprinc -randkey zkclient/quickstart.confluent.io@TEST.CONFLUENT.IO"
      docker exec -it kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab zkclient/quickstart.confluent.io@TEST.CONFLUENT.IO"
    done

   For Kafka brokers, the principal should be called ``kafka``.

   .. sourcecode:: bash

    for principal in broker1 broker2 broker3
    do
      docker exec -it kerberos kadmin.local -q "addprinc -randkey kafka/quickstart.confluent.io@TEST.CONFLUENT.IO"
      docker exec -it kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab kafka/quickstart.confluent.io@TEST.CONFLUENT.IO"
    done

   .. sourcecode:: bash

    for principal in saslproducer saslconsumer
    do
      docker exec -it kerberos kadmin.local -q "addprinc -randkey ${principal}/quickstart.confluent.io@TEST.CONFLUENT.IO"
      docker exec -it kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab ${principal}/quickstart.confluent.io@TEST.CONFLUENT.IO"
    done

#. Run a 3-node |zk| ensemble with SASL enabled.

   .. sourcecode:: bash

       docker run -d \
           --net=host \
           --name=zk-sasl-1 \
           -e ZOOKEEPER_SERVER_ID=1 \
           -e ZOOKEEPER_CLIENT_PORT=22181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           -e ZOOKEEPER_INIT_LIMIT=5 \
           -e ZOOKEEPER_SYNC_LIMIT=2 \
           -e ZOOKEEPER_SERVERS="quickstart.confluent.io:22888:23888;quickstart.confluent.io:32888:33888;quickstart.confluent.io:42888:43888" \
           -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/zookeeper_1_jaas.conf  -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf -Dzookeeper.authProvider.1=org.apache.zookeeper.server.auth.SASLAuthenticationProvider -Dsun.security.krb5.debug=true" \
           -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
           confluentinc/cp-zookeeper:4.1.4

   .. sourcecode:: bash

       docker run -d \
           --net=host \
           --name=zk-sasl-2 \
           -e ZOOKEEPER_SERVER_ID=2 \
           -e ZOOKEEPER_CLIENT_PORT=32181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           -e ZOOKEEPER_INIT_LIMIT=5 \
           -e ZOOKEEPER_SYNC_LIMIT=2 \
           -e ZOOKEEPER_SERVERS="quickstart.confluent.io:22888:23888;quickstart.confluent.io:32888:33888;quickstart.confluent.io:42888:43888" \
           -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/zookeeper_2_jaas.conf  -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf  -Dzookeeper.authProvider.1=org.apache.zookeeper.server.auth.SASLAuthenticationProvider -Dsun.security.krb5.debug=true" \
           -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
           confluentinc/cp-zookeeper:4.1.4

   .. sourcecode:: bash

       docker run -d \
           --net=host \
           --name=zk-sasl-3 \
           -e ZOOKEEPER_SERVER_ID=3 \
           -e ZOOKEEPER_CLIENT_PORT=42181 \
           -e ZOOKEEPER_TICK_TIME=2000 \
           -e ZOOKEEPER_INIT_LIMIT=5 \
           -e ZOOKEEPER_SYNC_LIMIT=2 \
           -e ZOOKEEPER_SERVERS="quickstart.confluent.io:22888:23888;quickstart.confluent.io:32888:33888;quickstart.confluent.io:42888:43888" \
           -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/zookeeper_3_jaas.conf  -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf  -Dzookeeper.authProvider.1=org.apache.zookeeper.server.auth.SASLAuthenticationProvider -Dsun.security.krb5.debug=true" \
           -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
           confluentinc/cp-zookeeper:4.1.4

   Check the logs to see the |zk| server has booted up successfully

   .. sourcecode:: bash

     docker logs zk-sasl-1

   You should see messages like this at the end of the log output:

   .. sourcecode:: bash

     [2016-07-24 07:17:50,960] INFO Created server with tickTime 2000 minSessionTimeout 4000 maxSessionTimeout 40000 datadir /var/lib/zookeeper/log/version-2 snapdir /var/lib/zookeeper/data/version-2 (org.apache.zookeeper.server.ZooKeeperServer)
     [2016-07-24 07:17:50,961] INFO FOLLOWING - LEADER ELECTION TOOK - 21823 (org.apache.zookeeper.server.quorum.Learner)
     [2016-07-24 07:17:50,983] INFO Getting a diff from the leader 0x0 (org.apache.zookeeper.server.quorum.Learner)
     [2016-07-24 07:17:50,986] INFO Snapshotting: 0x0 to /var/lib/zookeeper/data/version-2/snapshot.0 (org.apache.zookeeper.server.persistence.FileTxnSnapLog)
     [2016-07-24 07:17:52,803] INFO Received connection request /127.0.0.1:50056 (org.apache.zookeeper.server.quorum.QuorumCnxManager)
     [2016-07-24 07:17:52,806] INFO Notification: 1 (message format version), 3 (n.leader), 0x0 (n.zxid), 0x1 (n.round), LOOKING (n.state), 3 (n.sid), 0x0 (n.peerEpoch) FOLLOWING (my state) (org.apache.zookeeper.server.quorum.FastLeaderElection)

   You can repeat the command for the two other |zk| nodes.  Next, you should verify that ZK ensemble is ready:

   .. sourcecode:: bash

     for i in 22181 32181 42181; do
        docker run --net=host --rm confluentinc/cp-zookeeper:4.1.4 bash -c "echo stat | nc quickstart.confluent.io $i | grep Mode"
     done

   You should see one ``leader`` and two ``follower`` instances.

   .. sourcecode:: bash

     Mode: follower
     Mode: leader
     Mode: follower

#. Now that |zk| is up and running, we can fire up a three node Kafka cluster.

   .. sourcecode:: bash

      docker run -d \
         --net=host \
         --name=kafka-sasl-1 \
         -e KAFKA_ZOOKEEPER_CONNECT="quickstart.confluent.io:22181,quickstart.confluent.io:32181,quickstart.confluent.io:42181" \
         -e KAFKA_ADVERTISED_LISTENERS=SASL_SSL://quickstart.confluent.io:29094 \
         -e KAFKA_SSL_KEYSTORE_FILENAME=kafka.broker1.keystore.jks \
         -e KAFKA_SSL_KEYSTORE_CREDENTIALS=broker1_keystore_creds \
         -e KAFKA_SSL_KEY_CREDENTIALS=broker1_sslkey_creds \
         -e KAFKA_SSL_TRUSTSTORE_FILENAME=kafka.broker1.truststore.jks \
         -e KAFKA_SSL_TRUSTSTORE_CREDENTIALS=broker1_truststore_creds \
         -e KAFKA_SECURITY_INTER_BROKER_PROTOCOL=SASL_SSL \
         -e KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL=GSSAPI \
         -e KAFKA_SASL_ENABLED_MECHANISMS=GSSAPI \
         -e KAFKA_SASL_KERBEROS_SERVICE_NAME=kafka \
         -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
         -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/broker1_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf -Dsun.security.krb5.debug=true" \
          confluentinc/cp-kafka:4.1.4

   .. sourcecode:: bash

      docker run -d \
         --net=host \
         --name=kafka-sasl-2 \
         -e KAFKA_ZOOKEEPER_CONNECT=quickstart.confluent.io:22181,quickstart.confluent.io:32181,quickstart.confluent.io:42181 \
         -e KAFKA_ADVERTISED_LISTENERS=SASL_SSL://quickstart.confluent.io:39094 \
         -e KAFKA_SSL_KEYSTORE_FILENAME=kafka.broker2.keystore.jks \
         -e KAFKA_SSL_KEYSTORE_CREDENTIALS=broker2_keystore_creds \
         -e KAFKA_SSL_KEY_CREDENTIALS=broker2_sslkey_creds \
         -e KAFKA_SSL_TRUSTSTORE_FILENAME=kafka.broker2.truststore.jks \
         -e KAFKA_SSL_TRUSTSTORE_CREDENTIALS=broker2_truststore_creds \
         -e KAFKA_SECURITY_INTER_BROKER_PROTOCOL=SASL_SSL \
         -e KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL=GSSAPI \
         -e KAFKA_SASL_ENABLED_MECHANISMS=GSSAPI \
         -e KAFKA_SASL_KERBEROS_SERVICE_NAME=kafka \
         -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
         -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/broker2_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf -Dsun.security.krb5.debug=true" \
          confluentinc/cp-kafka:4.1.4

   .. sourcecode:: bash

      docker run -d \
         --net=host \
         --name=kafka-sasl-3 \
         -e KAFKA_ZOOKEEPER_CONNECT=quickstart.confluent.io:22181,quickstart.confluent.io:32181,quickstart.confluent.io:42181 \
         -e KAFKA_ADVERTISED_LISTENERS=SASL_SSL://quickstart.confluent.io:49094 \
         -e KAFKA_SSL_KEYSTORE_FILENAME=kafka.broker3.keystore.jks \
         -e KAFKA_SSL_KEYSTORE_CREDENTIALS=broker3_keystore_creds \
         -e KAFKA_SSL_KEY_CREDENTIALS=broker3_sslkey_creds \
         -e KAFKA_SSL_TRUSTSTORE_FILENAME=kafka.broker3.truststore.jks \
         -e KAFKA_SSL_TRUSTSTORE_CREDENTIALS=broker3_truststore_creds \
         -e KAFKA_SECURITY_INTER_BROKER_PROTOCOL=SASL_SSL \
         -e KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL=GSSAPI \
         -e KAFKA_SASL_ENABLED_MECHANISMS=GSSAPI \
         -e KAFKA_SASL_KERBEROS_SERVICE_NAME=kafka \
         -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
         -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/broker3_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf -Dsun.security.krb5.debug=true" \
          confluentinc/cp-kafka:4.1.4


   Check the logs to see the broker has booted up successfully:

   .. sourcecode:: bash

      docker logs kafka-sasl-1
      docker logs kafka-sasl-2
      docker logs kafka-sasl-3

   You should see start see bootup messages. For example, ``docker logs kafka-sasl-3 | grep started`` should show the following:

   .. sourcecode:: bash

      [2016-07-24 07:29:20,258] INFO [Kafka Server 1003], started (kafka.server.KafkaServer)
      [2016-07-24 07:29:20,258] INFO [Kafka Server 1003], started (kafka.server.KafkaServer)

   You should see the messages like the following on the broker acting as controller.

   .. sourcecode:: bash

      [2016-07-24 07:29:20,283] TRACE Controller 1001 epoch 1 received response {error_code=0} for a request sent to broker localhost:29092 (id: 1001 rack: null) (state.change.logger)
      [2016-07-24 07:29:20,283] TRACE Controller 1001 epoch 1 received response {error_code=0} for a request sent to broker localhost:29092 (id: 1001 rack: null) (state.change.logger)
      [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
      [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
      [2016-07-24 07:29:20,286] INFO [Controller-1001-to-broker-1003-send-thread], Starting  (kafka.controller.RequestSendThread)
      [2016-07-24 07:29:20,287] INFO [Controller-1001-to-broker-1003-send-thread], Controller 1001 connected to localhost:49092 (id: 1003 rack: null) for sending state change requests (kafka.controller.RequestSendThread)

#. Test that the broker is working as expected.

   Now that the brokers are up, we'll test that they're working as expected by creating a topic.

   .. sourcecode:: bash

      docker run \
        --net=host \
        --rm \
        -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
        -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/broker1_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf" \
        confluentinc/cp-kafka:4.1.4 \
        kafka-topics --create --topic bar --partitions 3 --replication-factor 3 --if-not-exists --zookeeper quickstart.confluent.io:32181

   You should see the following output:

   .. sourcecode:: bash

    Created topic "bar".

   Now verify that the topic is created successfully by describing the topic.

   .. sourcecode:: bash

       docker run \
          --net=host \
          --rm \
          -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
          -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/broker3_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf" \
          confluentinc/cp-kafka:4.1.4 \
          kafka-topics --describe --topic bar --zookeeper quickstart.confluent.io:32181

   You should see the following message in your terminal window:

   .. sourcecode:: bash

       Topic:bar   PartitionCount:3    ReplicationFactor:3 Configs:
       Topic: bar  Partition: 0    Leader: 1003    Replicas: 1003,1002,1001    Isr: 1003,1002,1001
       Topic: bar  Partition: 1    Leader: 1001    Replicas: 1001,1003,1002    Isr: 1001,1003,1002
       Topic: bar  Partition: 2    Leader: 1002    Replicas: 1002,1001,1003    Isr: 1002,1001,1003

   Next, you can try generating some data to the ``bar`` topic that was just created.

   .. sourcecode:: bash

        docker run \
          --net=host \
          --rm \
          -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
          -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/producer_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf" \
          confluentinc/cp-kafka:4.1.4 \
          bash -c "seq 42 | kafka-console-producer --broker-list quickstart.confluent.io:29094 --topic bar --producer.config /etc/kafka/secrets/host.producer.ssl.sasl.config && echo 'Produced 42 messages.'"

   The command above will pass 42 integers using the Console Producer that is shipped with Kafka.  As a result, you should see something like this in your terminal:

   .. sourcecode:: bash

      Produced 42 messages.

   It looked like things were successfully written, but let's try reading the messages back using the Console Consumer and make sure they're all accounted for.

   .. sourcecode:: bash

      docker run \
        --net=host \
        --rm \
        -v ${KAFKA_SASL_SECRETS_DIR}:/etc/kafka/secrets \
        -e KAFKA_OPTS="-Djava.security.auth.login.config=/etc/kafka/secrets/consumer_jaas.conf -Djava.security.krb5.conf=/etc/kafka/secrets/krb.conf" \
        confluentinc/cp-kafka:4.1.4 \
        kafka-console-consumer --bootstrap-server quickstart.confluent.io:29094 --topic bar --new-consumer --from-beginning --consumer.config /etc/kafka/secrets/host.consumer.ssl.sasl.config

   You should see the following (it might take some time for this command to return data. Kafka has to create the ``__consumers_offset`` topic behind the scenes when you consume data for the first time and this may take some time):

   .. sourcecode:: bash

       1
       4
       7
       10
       13
       16
       ....
       41
       Processed a total of 42 messages

.. _clustered_quickstart_compose_sasl :

Docker Compose: Setting Up a Three Node Confluent Platform Cluster with SASL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you get started, you will first need to install `Docker <https://docs.docker.com/engine/installation/>`_ and `Docker Compose <https://docs.docker.com/compose/install/>`_.  Once you've done that, you can follow the steps below to start up the Confluent Platform services.

#. Follow sections 1, 2 and 3 in :ref:`docker-client-setup-3-node-sasl` to create a docker-machine and generate the SSL credentials.

   Set the environment variable for secrets directory. This is used in the compose file.

   .. sourcecode:: bash

    export KAFKA_SASL_SECRETS_DIR=$(pwd)/examples/kafka-cluster-sasl/secrets
    
#. Build the Kerberos image

   .. sourcecode:: bash

    cd tests/images/kerberos
    docker build -t confluentinc/cp-kerberos:latest .

#. Start Kerberos

   Make sure you are in the ``cp-docker-images`` directory.
  
   .. sourcecode:: bash

       docker-compose create kerberos
       docker-compose start kerberos

#. Create keytabs and principals.

   i. Follow steps 3.1 above to make sure ``quickstart.confluent.io`` is resolvable.

   ii. Now, lets create all the principals and their keytabs on Kerberos.

       .. sourcecode:: bash

        for principal in zookeeper1 zookeeper2 zookeeper3
        do
          docker-compose exec kerberos kadmin.local -q "addprinc -randkey zookeeper/quickstart.confluent.io@TEST.CONFLUENT.IO"
          docker-compose exec kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab zookeeper/quickstart.confluent.io@TEST.CONFLUENT.IO"
        done

       .. sourcecode:: bash

        for principal in zkclient1 zkclient2 zkclient3
        do
          docker-compose exec kerberos kadmin.local -q "addprinc -randkey zkclient/quickstart.confluent.io@TEST.CONFLUENT.IO"
          docker-compose exec kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab zkclient/quickstart.confluent.io@TEST.CONFLUENT.IO"
        done

        For Kafka brokers, the principal should be called ``kafka``.

        .. sourcecode:: bash

            for principal in broker1 broker2 broker3
            do
              docker-compose exec kerberos kadmin.local -q "addprinc -randkey kafka/quickstart.confluent.io@TEST.CONFLUENT.IO"
              docker-compose exec kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab kafka/quickstart.confluent.io@TEST.CONFLUENT.IO"
            done

        .. sourcecode:: bash

            for principal in saslproducer saslconsumer
            do
              docker-compose exec kerberos kadmin.local -q "addprinc -randkey ${principal}/quickstart.confluent.io@TEST.CONFLUENT.IO"
              docker-compose exec kerberos kadmin.local -q "ktadd -norandkey -k /tmp/keytab/${principal}.keytab ${principal}/quickstart.confluent.io@TEST.CONFLUENT.IO"
            done


#. Start |zk| and Kafka

   .. sourcecode:: bash

       docker-compose create
       docker-compose start

   Before we move on, let's make sure the services are up and running:

   .. sourcecode:: bash

       docker-compose ps

   You should see the following:

   .. sourcecode:: bash

      Name                            Command            State   Ports
    -------------------------------------------------------------------------------
    kafkaclustersasl_kafka-sasl-1_1       /etc/confluent/docker/run   Up
    kafkaclustersasl_kafka-sasl-2_1       /etc/confluent/docker/run   Up
    kafkaclustersasl_kafka-sasl-3_1       /etc/confluent/docker/run   Up
    kafkaclustersasl_kerberos_1           /config.sh                  Up
    kafkaclustersasl_zookeeper-sasl-1_1   /etc/confluent/docker/run   Up
    kafkaclustersasl_zookeeper-sasl-2_1   /etc/confluent/docker/run   Up
    kafkaclustersasl_zookeeper-sasl-3_1   /etc/confluent/docker/run   Up

   Check the |zk| logs to verify that |zk| is healthy. For example, for service zookeeper-1:

   .. sourcecode:: bash

      docker-compose logs zookeeper-sasl-1

   You should see messages like the following:

   .. sourcecode:: bash

      zookeeper-1_1  | [2016-07-25 04:58:12,901] INFO Created server with tickTime 2000 minSessionTimeout 4000 maxSessionTimeout 40000 datadir /var/lib/zookeeper/log/version-2 snapdir /var/lib/zookeeper/data/version-2 (org.apache.zookeeper.server.ZooKeeperServer)
      zookeeper-1_1  | [2016-07-25 04:58:12,902] INFO FOLLOWING - LEADER ELECTION TOOK - 235 (org.apache.zookeeper.server.quorum.Learner)

   Verify that |zk| ensemble is ready.

   .. sourcecode:: bash

       for i in 22181 32181 42181; do
          docker run --net=host --rm confluentinc/cp-zookeeper:4.1.4 bash -c "echo stat | nc quickstart.confluent.io $i | grep Mode"
       done

   You should see one ``leader`` and two ``follower`` instances:

   .. sourcecode:: bash

      Mode: follower
      Mode: leader
      Mode: follower

   Check the logs to see the broker has booted up successfully

   .. sourcecode:: bash

      docker-compose logs kafka-sasl-1
      docker-compose logs kafka-sasl-2
      docker-compose logs kafka-sasl-3

   You should start seeing bootup messages. For example, ``docker-compose logs kafka-sasl-3 | grep started`` shows the following

   .. sourcecode:: bash

      kafka-sasl-3_1      | [2016-07-25 04:58:15,189] INFO [Kafka Server 3], started (kafka.server.KafkaServer)
      kafka-sasl-3_1      | [2016-07-25 04:58:15,189] INFO [Kafka Server 3], started (kafka.server.KafkaServer)

   You should see the messages like the following on the broker acting as controller.

   .. tip:: `docker-compose logs | grep controller` makes it easy to grep through logs for all services.

   .. sourcecode:: bash

      kafka-sasl-1_1      | [2016-09-01 08:48:42,585] INFO [Controller-1-to-broker-2-send-thread], Starting  (kafka.controller.RequestSendThread)
      kafka-sasl-2_1      | [2016-09-01 08:48:41,716] INFO [Controller 2]: Controller startup complete (kafka.controller.KafkaController)
      kafka-sasl-1_1      | [2016-09-01 08:48:42,585] INFO [Controller-1-to-broker-2-send-thread], Starting  (kafka.controller.RequestSendThread)
      kafka-sasl-2_1      | [2016-09-01 08:48:41,716] INFO [Controller 2]: Controller startup complete (kafka.controller.KafkaController)
      kafka-sasl-2_1      | [2016-09-01 08:48:41,716] INFO [Controller 2]: Controller startup complete (kafka.controller.KafkaController)

#. Follow step 8 in :ref:`docker-client-setup-3-node-sasl` to test that your brokers are functioning as expected.

#. To stop the cluster, first stop Kafka nodes one-by-one and then stop the |zk| cluster.

   .. sourcecode:: bash

    docker-compose stop kafka-sasl-1
    docker-compose stop kafka-sasl-2
    docker-compose stop kafka-sasl-3
    docker-compose stop
    docker-compose rm
