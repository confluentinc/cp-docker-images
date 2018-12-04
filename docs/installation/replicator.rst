.. _replicator:

Replicator Tutorial on Docker
=============================

This topic provides a tutorial for running Replicator to replicate data between Kafka clusters ``dc1`` and ``dc2``. It uses provenance headers to prevent cyclic replication of topic data.

.. include:: includes/start-download.rst

#.  Clone the Docker images repository, checkout the |release| branch, and navigate to the directory with the multi-datacenter example.

    .. codewithvars:: bash

        git clone https://github.com/confluentinc/cp-docker-images
        git checkout |release_post_branch|
        cd cp-docker-images/examples/multi-datacenter/

#.  Start the services by using the example Docker Compose file. It will start up 2 source Kafka clusters, one destination
    Kafka cluster and a |kconnect| cluster.

    ::

        docker-compose up -d

    This starts the |cp| with separate containers for all |cp| components. Your output should resemble the following:

    ::

        Creating zookeeper-dc1 ... done
        Creating zookeeper-dc2 ... done
        Creating broker-dc2    ... done
        Creating broker-dc1    ... done
        Creating schema-registry-dc1 ... done
        Creating schema-registry-dc2 ... done
        Creating datagen-dc1           ... done
        Creating datagen-dc2           ... done
        Creating replicator-dc1-to-dc2 ... done
        Creating replicator-dc2-to-dc1 ... done

#. Wait at least 1 minute for the services to come up.


Step 2: Create a Kafka topic with data
--------------------------------------

In this step, you create ``mytopic`` in origin cluster ``dc1``.

#.  Create a topic named ``mytopic`` in ``dc1``.

    .. codewithvars:: bash

        docker-compose exec broker-dc1 \
        kafka-topics --create --topic mytopic --zookeeper zookeeper-dc1:2181 --partitions 1 --replication-factor 1

    You should see the following output in your terminal window:

    .. codewithvars:: bash

     Created topic "mytopic".


#.  Generate data to ``mytopic`` in ``dc1``. The sequence of these messages is 1 to 100.

    .. codewithvars:: bash

        docker-compose exec broker-dc1 \
        bash -c "seq 100 | kafka-console-producer --request-required-acks 1 --broker-list \
        broker-dc1:9091 --topic mytopic && echo 'Produced 100 messages.'" 

    This command will use the built-in Kafka Console Producer to produce 100 simple messages to the topic. After running,
    you should see the following:

    .. codewithvars:: bash

      >>>>>>>>>>>>>>>>>>>>Produced 100 messages.


Step 3: Setup Data Replication
------------------------------

In this step, you try out some common operations. Now that the connector is up and running, it should replicate data from
``mytopic`` topic on ``dc1`` cluster to ``mytopic`` topic on ``dc2`` cluster.

#.  Create the connector using the Kafka Connect REST API. This replicates data from ``dc1`` to ``dc2``, with provenance headers enabled.

    .. codewithvars:: bash
 
            curl -X POST \
                 -H "Content-Type: application/json" \
                 --data '{
                       "name": "replicator-dc1-to-dc2",
                       "config": {
                         "connector.class": "io.confluent.connect.replicator.ReplicatorSourceConnector",
                         "topic.whitelist": "mytopic",
                         "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                         "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                         "src.kafka.bootstrap.servers": "broker-dc1:9091",
                         "src.consumer.group.id": "replicator-dc1-to-dc2",
                         "src.kafka.timestamps.producer.interceptor.classes": "io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor",
                         "src.kafka.timestamps.producer.confluent.monitoring.interceptor.bootstrap.servers": "broker-dc1:9091",
                         "dest.kafka.bootstrap.servers": "broker-dc2:9092",
                         "dest.kafka.replication.factor": 1,
                         "provenance.header.enable": "true",
                         "header.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                         "tasks.max": "1"
                       }}' \
                 http://localhost:8382/connectors

#.  Verify that the Confluent Replicator connector is running using the Kafka Connect REST API.

    .. codewithvars:: bash

            curl http://localhost:8382/connectors/replicator-dc1-to-dc2


#.  Read a sample of 100 records from the ``mytopic`` topic in the cluster ``dc2``. Recall that you produced data to this topic in ``dc1``, so reading it in ``dc2`` means that Replicator copied that data to ``dc2``.

    .. codewithvars:: bash

        docker-compose exec broker-dc2 kafka-console-consumer --bootstrap-server broker-dc2:9092 --topic mytopic \
        --from-beginning --max-messages 100

    If everything is working as expected, each of the original messages you produced should be written back out:

    .. codewithvars:: bash

        1
        ....
        100
        Processed a total of 100 messages


Step 4: Verify Prevention of Cyclic Replication of Data
-------------------------------------------------------

In this step, you replicate data from ``mytopic`` topic on ``dc2`` cluster to ``mytopic`` topic on ``dc1`` cluster.

#.  Create the connector using the Kafka Connect REST API. This replicates data from ``dc1`` to ``dc2``, with provenance headers enabled.

    .. codewithvars:: bash

            curl -X POST \
                 -H "Content-Type: application/json" \
                 --data '{
                       "name": "replicator-dc2-to-dc1",
                       "config": {
                         "connector.class": "io.confluent.connect.replicator.ReplicatorSourceConnector",
                         "topic.whitelist": "mytopic",
                         "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                         "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                         "src.kafka.bootstrap.servers": "broker-dc2:9092",
                         "src.consumer.group.id": "replicator-dc2-to-dc1",
                         "src.kafka.timestamps.producer.interceptor.classes": "io.confluent.monitoring.clients.interceptor.MonitoringProducerInterceptor",
                         "src.kafka.timestamps.producer.confluent.monitoring.interceptor.bootstrap.servers": "broker-dc2:9092",
                         "dest.kafka.bootstrap.servers": "broker-dc1:9091",
                         "dest.kafka.replication.factor": 1,
                         "provenance.header.enable": "true",
                         "header.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                         "tasks.max": "1"
                       }}' \
                 http://localhost:8381/connectors

#.  Generate data to ``mytopic`` in ``dc2``. The sequence of these messages is 101 to 200.

    .. codewithvars:: bash

        docker-compose exec broker-dc2 \
        bash -c "seq 101 200 | kafka-console-producer --request-required-acks 1 --broker-list \
        broker-dc2:9092 --topic mytopic && echo 'Produced 100 messages.'" 

    This command will use the built-in Kafka Console Producer to produce 100 simple messages to the topic. After running,
    you should see the following:

    .. codewithvars:: bash

      >>>>>>>>>>>>>>>>>>>>Produced 100 messages.

#.  Read a sample of 200 records from the ``mytopic`` topic in the cluster ``dc1``. Recall that you produced data to this topic in ``dc1`` (seq 1-100) and ``dc1`` (seq 101-200).

    .. codewithvars:: bash

        docker-compose exec broker-dc1 kafka-console-consumer --bootstrap-server broker-dc1:9091 --topic mytopic \
        --from-beginning --max-messages 200

    If everything is working as expected, each of the original messages you produced should be written back out:

    .. codewithvars:: bash

        1
        ....
        200
        Processed a total of 200 messages

#.  Read a sample of 100 records from the ``mytopic`` topic in the cluster ``dc2``, instead of ``dc1`` as done in the previous step.

    .. codewithvars:: bash

        docker-compose exec broker-dc2 kafka-console-consumer --bootstrap-server broker-dc2:9092 --topic mytopic \
        --from-beginning --max-messages 200

    If everything is working as expected, each of the original messages you produced should be written back out:
    
    .. codewithvars:: bash

        1
        ....
        200
        Processed a total of 200 messages


Step 5: Shutdown and Cleanup
----------------------------

Use the following commands to shutdown all the components.

.. codewithvars:: bash

    docker-compose stop

If you want to remove all the containers, run:

.. codewithvars:: bash

    docker-compose rm
