.. _replicator:

Replicator Tutorial on Docker
=============================

This topic provides a tutorial for running Replicator which replicates data from two source Kafka clusters to a
destination Kafka cluster.  By the end of this tutorial, you will have successfully run Replicator and replicated data
for two topics from different source clusters to a destination cluster.  Furthermore, you will have also set up a Kafka
Connect cluster because Replicator is built on Connect.

Prerequisites:
    - .. include:: ../includes/docker-version.rst
    - Git


Step 1: Download and Start |cp| Using Docker
--------------------------------------------

#.  In `Docker’s advanced settings <https://docs.docker.com/docker-for-mac/#advanced>`__, increase the memory dedicated
    to Docker to at least 8 GB (default is 2 GB).
#.  Clone the Docker images repository, navigate to the examples directory, and checkout the |release| branch.

    .. codewithvars:: bash

        git clone https://github.com/confluentinc/cp-docker-images
        cd cp-docker-images/examples/enterprise-replicator/
        git checkout |release_post_branch|

#.  Start the services by using the example Docker Compose file. It will start up 2 source Kafka clusters, one destination
    Kafka cluster and a |kconnect| cluster. Start |cp| specifying two options: (``-d``) to run in detached mode and
    (``--build``) to build the |kconnect| image with the source connector ``kafka-connect-datagen`` from Confluent Hub.

    ::

        docker-compose up -d --build

    This starts the |cp| with separate containers for all |cp| components. Your output should resemble the following:

    ::

        Creating enterprise-replicator_kafka-1-src-b_1_2d59a9341917   ... done
        Creating enterprise-replicator_kafka-2-src-b_1_610bf97f0961   ... done
        Creating enterprise-replicator_zookeeper-src-a_1_7444e5351db9 ... done
        Creating enterprise-replicator_kafka-1-dest_1_9f4ea8eec9af    ... done
        Creating enterprise-replicator_zookeeper-dest_1_ee4ad01c9bdc  ... done
        Creating enterprise-replicator_zookeeper-src-b_1_63b18c29c250 ... done
        Creating enterprise-replicator_connect-host-1_1_20ead4b0136c  ... done
        Creating enterprise-replicator_kafka-2-dest_1_1d843329379c    ... done
        Creating enterprise-replicator_connect-host-2_1_5fef8a9326ee  ... done
        Creating enterprise-replicator_kafka-1-src-a_1_e7b24f3b7237   ... done
        Creating enterprise-replicator_kafka-2-src-a_1_c02411cf47cb   ... done


Step 2: Create a Kafka Connect Replicator Connector
---------------------------------------------------

In this step, you create a :ref:`Kafka Connect Replicator connector <connect_replicator>` for replicating topic ``foo``
from source cluster ``source-a``.


#.  Create a topic named ``foo``.

    .. codewithvars:: bash

        docker run \
          --net=host \
          --rm confluentinc/cp-kafka:|release| \
          kafka-topics --create --topic foo --partitions 3 --replication-factor 2 \
          --if-not-exists --zookeeper localhost:22181

    You should see the following output in your terminal window:

    .. codewithvars:: bash

     Created topic "foo".


#.  Generate some data to your new topic:

    .. codewithvars:: bash

        docker run \
          --net=host \
          --rm \
          confluentinc/cp-kafka:|release| \
          bash -c "seq 1000 | kafka-console-producer --request-required-acks 1 \
          --broker-list localhost:9092 --topic foo && echo 'Produced 1000 messages.'"

    This command will use the built-in Kafka Console Producer to produce 100 simple messages to the topic. After running,
    you should see the following:

    .. codewithvars:: bash

      Produced 1000 messages.

#.  Create the connector using the Kafka Connect REST API.

    #.  Exec into the Connect container.

        .. codewithvars:: bash

            docker-compose exec connect-host-1 bash

        You should see a bash prompt now. you will call this the ``docker exec`` command prompt:

        .. codewithvars:: bash

            root@confluent:/#

    #.   Create the Replicator connector. Run the following command on the ``docker exec`` command prompt.

         .. codewithvars:: bash

            curl -X POST \
                 -H "Content-Type: application/json" \
                 --data '{
                    "name": "replicator-src-a-foo",
                    "config": {
                      "connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector",
                      "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                      "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                      "src.zookeeper.connect": "localhost:22181",
                      "src.kafka.bootstrap.servers": "localhost:9092",
                      "dest.zookeeper.connect": "localhost:42181",
                      "topic.whitelist": "foo",
                      "topic.rename.format": "${topic}.replica"}}'  \
                 http://localhost:28082/connectors

         Upon running the command, you should see the following output in your ``docker exec`` command prompt:

         .. codewithvars:: bash

            {"name":"replicator-src-a-foo","config":{"connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector","key.converter":"io.confluent.connect.replicator.util.ByteArrayConverter","value.converter":"io.confluent.connect.replicator.util.ByteArrayConverter","src.zookeeper.connect":"localhost:22181","src.kafka.bootstrap.servers":"localhost:9092","dest.zookeeper.connect":"localhost:42181","topic.whitelist":"foo","topic.rename.format":"${topic}.replica","name":"replicator-src-a-foo"},"tasks":[]}


    #.  Exit the ``docker exec`` command prompt by typing ``exit`` on the prompt.

        .. codewithvars:: bash

            exit

Step 3: Try Out Replicator Operations
-------------------------------------

In this step, you try out some common operations. Now that the connector is up and running, it should replicate data from
``foo`` topic on ``source-a`` cluster to ``foo.replica`` topic on the ``dest`` cluster.

#.  Read a sample of 1000 records from the ``foo.replica`` topic to verify that the connector is replicating data to the
    destination Kafka cluster.

    .. tip:: You must have exited the ``docker exec`` command prompt before running this command.

    .. codewithvars:: bash

        docker run \
          --net=host \
          --rm \
          confluentinc/cp-kafka:|release| \
          kafka-console-consumer --bootstrap-server localhost:9072 --topic foo.replica --from-beginning --max-messages 1000

    If everything is working as expected, each of the original messages you produced should be written back out:

    .. codewithvars:: bash

        1
        ....
        1000
        Processed a total of 1000 messages

#.  Replicate another topic from a different source cluster.

    #.  Create a new topic on the cluster ``source-b`` and add some data to it. Run the following commands to create and verify the topic.
        You should see output similar to the previous steps:

        .. codewithvars:: bash

            docker run \
              --net=host \
              --rm confluentinc/cp-kafka:|release| \
              kafka-topics --create --topic bar --partitions 3 --replication-factor 2 --if-not-exists --zookeeper localhost:32181

        .. codewithvars:: bash

            docker run \
              --net=host \
              --rm confluentinc/cp-kafka:|release| \
              kafka-topics --describe --topic bar --zookeeper localhost:32181

        .. codewithvars:: bash

            docker run \
              --net=host \
              --rm \
              confluentinc/cp-kafka:|release| \
              bash -c "seq 1000 | kafka-console-producer --request-required-acks 1 --broker-list localhost:9082 --topic bar && echo 'Produced 1000 messages.'"

    #.  Exec into the Kafka Connect container and run the replicator connector. You should see output similar to the previous step.

        .. codewithvars:: bash

            docker-compose exec connect-host-1 bash

    #.  Run the following commands on the ``docker exec`` command prompt.

        .. codewithvars:: bash

            curl -X POST \
                 -H "Content-Type: application/json" \
                 --data '{
                    "name": "replicator-src-b-bar",
                    "config": {
                      "connector.class":"io.confluent.connect.replicator.ReplicatorSourceConnector",
                      "key.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                      "value.converter": "io.confluent.connect.replicator.util.ByteArrayConverter",
                      "src.zookeeper.connect": "localhost:32181",
                      "src.kafka.bootstrap.servers": "localhost:9082",
                      "dest.zookeeper.connect": "localhost:42181",
                      "topic.whitelist": "bar",
                      "topic.rename.format": "${topic}.replica"}}'  \
                 http://localhost:28082/connectors

        .. codewithvars:: bash

            curl -X GET http://localhost:28082/connectors/replicator-src-b-bar/status


    #.  Exit the ``docker exec`` command prompt.

        .. codewithvars:: bash

            exit

    Now that the second replicator connector is up and running, it should replicate data from ``bar`` topic on ``source-b`` cluster to ``bar.replica`` topic on the ``dest`` cluster.

#.  Read data from ``bar.replica`` topic to check if the connector is replicating data properly.

    .. codewithvars:: bash

            docker run \
              --net=host \
              --rm \
              confluentinc/cp-kafka:|release| \
              kafka-console-consumer --bootstrap-server localhost:9072 --topic bar.replica \
              --from-beginning --max-messages 1000

    Verify that the destination topic was created properly. You should see output similar to the
    previous step.

    .. codewithvars:: bash

            docker run \
              --net=host \
              --rm confluentinc/cp-kafka:|release| \
              kafka-topics --describe --topic bar.replica --zookeeper localhost:42181

Step 4: Shutdown and Cleanup
----------------------------

Use the following commands to shutdown all the components.

.. codewithvars:: bash

    docker-compose stop

If you want to remove all the containers, run:

.. codewithvars:: bash

    docker-compose rm
